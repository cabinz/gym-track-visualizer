"""Functions for synthesizing statistical (meta)data columns for visualization."""

from dataclasses import dataclass

from .common import *


class UMOConverter:
    def __init__(self, std_uom):
        self.std_uom = std_uom
        self._ratios = {}
        
        self.add_ratio('kg', 'lb', 2.20462)
    
    def add_ratio(self, src, tgt, ratio):
        self._ratios[src, tgt] = ratio
        self._ratios[tgt, src] = 1 / ratio
        
    def convert(self, value, src_uom, tgt_uom):
        if src_uom == tgt_uom:
            return value
        return value * self._ratios[src_uom, tgt_uom]
    
    def to_std(self, value, from_uom):
        return self.convert(value, from_uom, self.std_uom)


@dataclass
class MetaDataCols:
    """Column names of generated metadata."""
    TOT_CAP: str = 'tot_capacity'
    TGT_CAP: str = 'target_capacity'
    SUCC_SET_CAP: str = 'successful_set_capacity'
    FULL_SET_CAP: str = 'full_set_capacity'
    MAX_PASS_W: str = 'max_pass_set_weight'
    MAX_W: str = 'max_set_weight (maybe incomplete)'
    MIN_W: str = 'min_set_weight (maybe incomplete)'


@dataclass
class PreprocessConfig:
    """Configuration for preprocessing / analysis.

    Categorization of sets by reps:
    ====================================================================================
        Overloaded Set    |    Normal Progressing Set   |   Underloaded Set
                          |                             |
                    MIN_SET_REPS                    FULL_SET_REPS
    -----------------------------------------------------------------------> reps
    ====================================================================================
    """

    MIN_SET_REPS: int = 8
    """The minimum number of reps to consider a set as a "completed" set. Default as 8."""
    FULL_SET_REPS: int = 12
    """The number of reps to consider a set as a "full" set. Default as 12."""
    SET_ID_RANGE_L: int = 1
    """The lower bound (inclusive) of the set ID range that the preprocessing takes into account. 
    Default as 1."""
    SET_ID_RANGE_R: int = 4
    """The upper bound (inclusive) of the set ID range that the preprocessing takes into account.
    Default as 4."""
    WEIGHT_STD_UOM: str = 'kg'
    
    def __post_init__(self):
        self.converter = UMOConverter(self.WEIGHT_STD_UOM)

    def valid_set_num(self):
        """Get column names of set specified by global variables MIN_SET_NUM and MAX_SET_NUM.

        E.g. MIN_SET_NUM = 2, MAX_SET_NUM = 4
        -> Return [2, 3, 4]
        """
        return list(range(self.SET_ID_RANGE_L, self.SET_ID_RANGE_R + 1))
    
    def get_coln_weight_raw(self, i):
        return f'weight_{i}'
    
    def get_coln_weight(self, i):
        return f'weight_{i}_std ({self.converter.std_uom})'
    
    def get_coln_weight_std(self, i):
        return self.get_coln_weight(i)
    
    def get_coln_reps(self, i):
        return f'reps_{i}'

    def valid_set_cols_raw(self):
        """Get column names of set specified by global variables MIN_SET_NUM and MAX_SET_NUM.

        E.g. MIN_SET_NUM = 1, MAX_SET_NUM = 2
        -> Return [('weight_1', 'reps_1'), ('weight_2', 'reps_2')]
        """
        return [(self.get_coln_weight_raw(i), self.get_coln_reps(i)) for i in self.valid_set_num()]
    
    def valid_set_cols(self, ):
        """Get column names with standard weights of set specified by global variables MIN_SET_NUM and MAX_SET_NUM.

        E.g. MIN_SET_NUM = 1, MAX_SET_NUM = 2
        -> Return [('weight_1_std', 'reps_1'), ('weight_2_std', 'reps_2')]
        """
        return [(self.get_coln_weight(i), self.get_coln_reps(i)) for i in self.valid_set_num()]


DEFAULT_CONFIG = PreprocessConfig()
META_COLS = MetaDataCols()


def execute(df_data, config=DEFAULT_CONFIG):
    """Execute all registered proprocessing."""
    # Add invocation below to register a process. comment it out to cancel.
    df_data = standardize_weight(df_data, config)
    df_data = update_capacity(df_data, config)
    df_data = update_weight_boundaries(df_data, config)
    return df_data


def standardize_weight(df_data, config=DEFAULT_CONFIG):
    """Standardize weight columns to the standard unit of measurement."""
    # TODO: current standardization is a naive implementation.
    # It should be run before any other preprocessing to ensure
    # update standard weight using corresponding config (valid set id).
    # It should be replaced by a better implementation to be run once at the loading time.
    for i in config.valid_set_num():
        col_raw_weight_i = config.get_coln_weight_raw(i)
        col_std_weight_i = config.get_coln_weight(i)
        
        def convert(row):
            row[col_std_weight_i] = config.converter.to_std(
                row[col_raw_weight_i], row[COL_UOM])
            return row

        df_data = df_data.apply(lambda x: convert(x), axis=1)
    return df_data


def update_capacity(df_data, config=DEFAULT_CONFIG):
    """Update COL_TOT_CAPACITY, COL_COMPLETED_SET_CAPACITY, COL_FULL_SET_CAPACITY columns."""
    df_data = standardize_weight(df_data, config)
    df_data.loc[:, (META_COLS.TOT_CAP, META_COLS.SUCC_SET_CAP,
                    META_COLS.FULL_SET_CAP)] = 0
    for col_weight, col_reps in config.valid_set_cols():
        df_data = df_data.fillna({col_weight: 0, col_reps: 0})
        c = df_data[col_weight] * df_data[col_reps]
        df_data[META_COLS.TOT_CAP] += c
        df_data.loc[df_data[col_reps] >=
                    config.MIN_SET_REPS, META_COLS.SUCC_SET_CAP] += c
        df_data.loc[df_data[col_reps] >=
                    config.FULL_SET_REPS, META_COLS.FULL_SET_CAP] += c
    return df_data


def update_weight_boundaries(df_data, config=DEFAULT_CONFIG):
    """Update COL_MIN/MAX_SET columns.

    Note that the values are min/max weight among all "completed" sets (with reps exceeding the threshold).
    """
    # Initialize
    df_data = standardize_weight(df_data, config)
    df_data[META_COLS.MAX_PASS_W] = 0.0
    df_data[META_COLS.MAX_W] = 0.0
    df_data[META_COLS.MIN_W] = float('inf')

    # Update
    weight_cols, reps_cols = zip(*config.valid_set_cols())
    df_data.loc[:, META_COLS.MAX_W] = df_data.loc[:, weight_cols].max(axis=1)
    df_data.loc[:, META_COLS.MIN_W] = df_data.loc[:, weight_cols].min(axis=1)
    # Select rows where the number of reps is greater than or equal to the minimum threshold
    # Then update the max weight for these rows
    for col_weight, col_reps in config.valid_set_cols():
        cond_completed_set = df_data[col_reps] >= config.MIN_SET_REPS
        df_data.loc[cond_completed_set, META_COLS.MAX_PASS_W] = df_data.loc[
            cond_completed_set, [META_COLS.MAX_PASS_W, col_weight]].max(axis=1)

    df_data[META_COLS.TGT_CAP] = df_data[META_COLS.MAX_PASS_W] * \
        config.FULL_SET_REPS * (config.SET_ID_RANGE_R -
                                config.SET_ID_RANGE_L + 1)

    return df_data

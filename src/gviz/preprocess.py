"""Functions for synthesizing statistical (meta)data columns for visualization."""

from dataclasses import dataclass

from .common import *


@dataclass
class MetaDataCols:
    """Column names of generated metadata."""
    TOT_CAP: str = 'tot_capacity'
    TGT_CAP: str = 'target_capacity'
    SUCC_SET_CAP: str = 'successful_set_capacity'
    FULL_SET_CAP: str = 'full_set_capacity'
    MAX_PASS_W: str = 'max_pass_set_weight'
    MIN_PASS_W: str = 'min_pass_set_weight'


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

    def valid_set_num(self):
        """Get column names of set specified by global variables MIN_SET_NUM and MAX_SET_NUM.

        E.g. MIN_SET_NUM = 2, MAX_SET_NUM = 4
        -> Return [2, 3, 4]
        """
        return list(range(self.SET_ID_RANGE_L, self.SET_ID_RANGE_R + 1))

    def valid_set_cols(self):
        """Get column names of set specified by global variables MIN_SET_NUM and MAX_SET_NUM.

        E.g. MIN_SET_NUM = 1, MAX_SET_NUM = 2
        -> Return [('weight_1', 'reps_1'), ('weight_2', 'reps_2')]
        """
        ret = []
        for i in self.valid_set_num():
            col_weight, col_reps = f'weight_{i}', f'reps_{i}'
            ret.append((col_weight, col_reps))
        return ret


META_COLS = MetaDataCols()
DEFAULT_CONFIG = PreprocessConfig()


def execute(df_data, config=DEFAULT_CONFIG):
    """Execute all registered proprocessing."""
    # Add invocation below to register a process. comment it out to cancel.
    df_data = update_capacity(df_data, config)
    df_data = update_weight_boundaries(df_data, config)
    return df_data


def update_capacity(df_data, config=DEFAULT_CONFIG):
    """Update COL_TOT_CAPACITY, COL_COMPLETED_SET_CAPACITY, COL_FULL_SET_CAPACITY columns."""
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
    # Initialize the max valid weight for each row
    df_data[META_COLS.MAX_PASS_W] = 0.0
    df_data[META_COLS.MIN_PASS_W] = float('inf')

    # Iterate over the valid set columns
    for col_weight, col_reps in config.valid_set_cols():
        # Select rows where the number of reps is greater than or equal to the minimum threshold
        cond_completed_set = df_data[col_reps] >= config.MIN_SET_REPS
        # Update the max weight for these rows
        df_data.loc[cond_completed_set, META_COLS.MAX_PASS_W] = df_data.loc[
            cond_completed_set, [META_COLS.MAX_PASS_W, col_weight]].max(axis=1)
        df_data.loc[cond_completed_set, META_COLS.MIN_PASS_W] = df_data.loc[
            cond_completed_set, [META_COLS.MIN_PASS_W, col_weight]].min(axis=1)

    df_data[META_COLS.TGT_CAP] = df_data[META_COLS.MAX_PASS_W] * \
        config.FULL_SET_REPS * (config.SET_ID_RANGE_R -
                                config.SET_ID_RANGE_L + 1)

    return df_data

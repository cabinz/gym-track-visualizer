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
    
META_COLS = MetaDataCols()


def execute(df_data):
    """Execute all registered proprocessing."""
    # Add invocation below to register a process. comment it out to cancel.
    df_data = update_capacity(df_data)
    df_data = update_weight_boundaries(df_data)
    return df_data


def update_capacity(df_data):
    """Update COL_TOT_CAPACITY, COL_COMPLETED_SET_CAPACITY, COL_FULL_SET_CAPACITY columns."""
    df_data.loc[:, (META_COLS.TOT_CAP, META_COLS.SUCC_SET_CAP, META_COLS.FULL_SET_CAP)] = 0
    for col_weight, col_reps in valid_set_cols():
        df_data = df_data.fillna({col_weight: 0, col_reps: 0})
        c = df_data[col_weight] * df_data[col_reps]
        df_data[META_COLS.TOT_CAP] += c
        df_data.loc[df_data[col_reps] >= MIN_SET_REPS, META_COLS.SUCC_SET_CAP] += c
        df_data.loc[df_data[col_reps] >= FULL_SET_REPS, META_COLS.FULL_SET_CAP] += c
    return df_data


def update_weight_boundaries(df_data):
    """Update COL_MIN/MAX_SET columns.

    Note that the values are min/max weight among all "completed" sets (with reps exceeding the threshold).
    """
    # Initialize the max valid weight for each row
    df_data[META_COLS.MAX_PASS_W] = 0.0
    df_data[META_COLS.MIN_PASS_W] = float('inf')

    # Iterate over the valid set columns
    for col_weight, col_reps in valid_set_cols():
        # Select rows where the number of reps is greater than or equal to the minimum threshold
        cond_completed_set = df_data[col_reps] >= MIN_SET_REPS
        # Update the max weight for these rows
        df_data.loc[cond_completed_set, META_COLS.MAX_PASS_W] = df_data.loc[
            cond_completed_set, [META_COLS.MAX_PASS_W, col_weight]].max(axis=1)
        df_data.loc[cond_completed_set, META_COLS.MIN_PASS_W] = df_data.loc[
            cond_completed_set, [META_COLS.MIN_PASS_W, col_weight]].min(axis=1)

    df_data[META_COLS.TGT_CAP] = df_data[META_COLS.MAX_PASS_W] * FULL_SET_REPS * (SET_ID_RANGE_R - SET_ID_RANGE_L + 1)

    return df_data

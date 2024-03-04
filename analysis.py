"""Functions for synthesizing statistical (meta)data columns for visualization."""

from common import *


def update_analysis(df_data):
    """Execute all registered analysis and update the data in corresponding columns."""
    # Add invocation below to register a process. comment it out to cancel.
    df_data = update_capacity(df_data)
    df_data = update_weight_boundaries(df_data)
    return df_data


def update_capacity(df_data):
    """Update COL_TOT_CAPACITY, COL_COMPLETED_SET_CAPACITY, COL_FULL_SET_CAPACITY columns."""
    df_data.loc[:, (COL_TOT_CAP, COL_PASS_SET_CAP, COL_FULL_SET_CAP)] = 0
    for col_weight, col_reps in valid_set_cols():
        df_data = df_data.fillna({col_weight: 0, col_reps: 0})
        c = df_data[col_weight] * df_data[col_reps]
        df_data[COL_TOT_CAP] += c
        df_data.loc[df_data[col_reps] >= PASS_SET_REPS, COL_PASS_SET_CAP] += c
        df_data.loc[df_data[col_reps] >= FULL_SET_REPS, COL_FULL_SET_CAP] += c
    return df_data


def update_weight_boundaries(df_data, min_reps_per_set=PASS_SET_REPS):
    """Update COL_MIN/MAX_SET columns.

    Note that the values are min/max weight among all "completed" sets (with reps exceeding the threshold).
    """
    # Initialize the max valid weight for each row
    df_data[COL_MAX_PASS_W] = 0.0
    df_data[COL_MIN_PASS_W] = float('inf')

    # Iterate over the valid set columns
    for col_weight, col_reps in valid_set_cols():
        # Select rows where the number of reps is greater than or equal to the minimum threshold
        cond_completed_set = df_data[col_reps] >= min_reps_per_set
        # Update the max weight for these rows
        df_data.loc[cond_completed_set, COL_MAX_PASS_W] = df_data.loc[
            cond_completed_set, [COL_MAX_PASS_W, col_weight]].max(axis=1)
        df_data.loc[cond_completed_set, COL_MIN_PASS_W] = df_data.loc[
            cond_completed_set, [COL_MIN_PASS_W, col_weight]].min(axis=1)

    df_data[COL_TGT_CAP] = df_data[COL_MAX_PASS_W] * FULL_SET_REPS * (MAX_SET_NUM - MIN_SET_NUM + 1)

    return df_data


def get_active_days(df_data):
    """Retrieve the number of active (workout) days."""
    return df_data[COL_DATE].unique().shape[0]


if __name__ == '__main__':
    from data_loading import Loader

    ldr = Loader(TEST_FILE_PATH)
    df = ldr.get_records()
    df = update_analysis(df)
    print(df[:5])

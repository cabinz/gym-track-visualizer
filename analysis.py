"""Functions for synthesizing statistical (meta)data columns for visualization."""

from common import *


def update_analysis(df_data):
    """Execute all registered analysis and update the data in corresponding columns."""
    # Add invocation below to register a process. comment it out to cancel.
    df_data = update_capacity(df_data)
    df_data = update_max_set(df_data)
    return df_data


def _valid_set_cols():
    """Get column names of set specified by global variables MIN_SET_NUM and MAX_SET_NUM.

    E.g. MIN_SET_NUM = 1, MAX_SET_NUM = 2
    -> Return [('weight_1', 'reps_1'), ('weight_2', 'reps_2')]
    """
    ret = []
    for i in range(MIN_SET_NUM, MAX_SET_NUM + 1):
        col_weight, col_reps = f'weight_{i}', f'reps_{i}'
        ret.append((col_weight, col_reps))
    return ret


def update_capacity(df_data):
    df_data.loc[:, (COL_TOT_CAPACITY, COL_COMPLETED_SET_CAPACITY, COL_FULL_SET_CAPACITY)] = 0
    for col_weight, col_reps in _valid_set_cols():
        df_data = df_data.fillna({col_weight: 0, col_reps: 0})
        c = df_data[col_weight] * df_data[col_reps]
        df_data[COL_TOT_CAPACITY] += c
        df_data.loc[df_data[col_reps] >= SET_THRESHOLD, COL_COMPLETED_SET_CAPACITY] += c
        df_data.loc[df_data[col_reps] >= FULL_SET_REPS, COL_FULL_SET_CAPACITY] += c
    return df_data


def update_max_set(df_data, min_reps_per_set=SET_THRESHOLD):
    # Initialize the max valid weight for each row
    df_data[COL_MAX_SET_W] = 0.0
    df_data[COL_MIN_SET_W] = float('inf')

    # Iterate over the valid set columns
    for col_weight, col_reps in _valid_set_cols():
        # Select rows where the number of reps is greater than or equal to the minimum threshold
        cond_completed_set = df_data[col_reps] >= min_reps_per_set
        # Update the max weight for these rows
        df_data.loc[cond_completed_set, COL_MAX_SET_W] = df_data.loc[
            cond_completed_set, [COL_MAX_SET_W, col_weight]].max(axis=1)
        df_data.loc[cond_completed_set, COL_MIN_SET_W] = df_data.loc[
            cond_completed_set, [COL_MIN_SET_W, col_weight]].min(axis=1)
    return df_data


if __name__ == '__main__':
    from data_loading import Loader

    ldr = Loader(TEST_FILE_PATH)
    df = ldr.get_records()
    df = update_analysis(df)
    print(df[:5])

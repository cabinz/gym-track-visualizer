# Column names of input raw data.
COL_DATE = 'date'
COL_ITEM_NAME = 'name'
COL_GYM = 'gym'
COL_ORDER = 'order'

# Configurations.
"""Categorization of sets by reps:

    Overloaded Set    |    Normal Progressing Set   |   Underloaded Set
                      |                             |
                 MIN_SET_REPS                    FULL_SET_REPS
-----------------------------------------------------------------------> reps
"""
MIN_SET_REPS = 8    # a threshold (passing line) to exceed for being considered as a successful set
FULL_SET_REPS = 12  # ... to be a full set
SET_ID_RANGE_L = 1  # The left bound (inclusive) of set index that the visualization takes into account
SET_ID_RANGE_R = 4  # The right bound (inclusive) ...

TEST_FILE_PATH = r'test/file/path'


def valid_set_num():
    """Get column names of set specified by global variables MIN_SET_NUM and MAX_SET_NUM.

    E.g. MIN_SET_NUM = 2, MAX_SET_NUM = 4
    -> Return [2, 3, 4]
    """
    return list(range(SET_ID_RANGE_L, SET_ID_RANGE_R + 1))


def valid_set_cols():
    """Get column names of set specified by global variables MIN_SET_NUM and MAX_SET_NUM.

    E.g. MIN_SET_NUM = 1, MAX_SET_NUM = 2
    -> Return [('weight_1', 'reps_1'), ('weight_2', 'reps_2')]
    """
    ret = []
    for i in valid_set_num():
        col_weight, col_reps = f'weight_{i}', f'reps_{i}'
        ret.append((col_weight, col_reps))
    return ret


def get_num_active_days(df_data) -> int:
    """Retrieve the number of active (workout) days."""
    return df_data[COL_DATE].unique().shape[0]


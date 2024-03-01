# Column names of input raw data.
COL_DATE = 'date'
COL_ITEM_NAME = 'name'
COL_GYM = 'gym'
COL_ORDER = 'order'
# Column names of generated metadata.
COL_TOT_CAP = 'tot_capacity'
COL_TGT_CAP = 'target_capacity'
COL_PASS_SET_CAP = 'pass_set_capacity'
COL_FULL_SET_CAP = 'full_set_capacity'
COL_MAX_PASS_W = 'max_pass_set_weight'
COL_MIN_PASS_W = 'min_pass_set_weight'

# Configurations.
"""Categorization of sets by reps:

    Fail Set    |    Pass Set   |   Full Set
                |               |
         PASS_SET_REPS   FULL_SET_REPS
-----------------------------------------------> reps
"""
PASS_SET_REPS = 8  # a threshold (passing line) to exceed for being considered as a (pass) set
FULL_SET_REPS = 12  # to be a full set
MIN_SET_NUM = 1  # The min sequence number of sets that the visualization takes into account
MAX_SET_NUM = 4  # The max sequence number of sets that the visualization takes into account

TEST_FILE_PATH = r'test/file/path'


def valid_set_num():
    """Get column names of set specified by global variables MIN_SET_NUM and MAX_SET_NUM.

    E.g. MIN_SET_NUM = 2, MAX_SET_NUM = 4
    -> Return [2, 3, 4]
    """
    return list(range(MIN_SET_NUM, MAX_SET_NUM + 1))


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

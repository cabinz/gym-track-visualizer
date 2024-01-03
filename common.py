# Column names of input raw data.
COL_DATE = 'date'
COL_ITEM_NAME = 'name'
# Column names of generated metadata.
COL_TOT_CAPACITY = 'tot_capacity'
COL_COMPLETED_SET_CAPACITY = 'completed_set_capacity'
COL_FULL_SET_CAPACITY = 'full_set_capacity'
COL_MAX_SET_W = 'max_set_weight'
COL_MIN_SET_W = 'min_set_weight'

# Configurations.
SET_THRESHOLD = 8  # reps
FULL_SET_REPS = 12  # reps
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

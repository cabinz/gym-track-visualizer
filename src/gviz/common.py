# Column names of input raw data.
COL_DATE = 'date'
COL_ITEM_NAME = 'name'
COL_GYM = 'gym'
COL_ORDER = 'order'
COL_UOM = 'unit'

# Standard unit of measurement (UOM) for weight
WEIGHT_STD_UOM = 'kg'


def get_num_active_days(df_data) -> int:
    """Retrieve the number of active (workout) days."""
    return df_data[COL_DATE].unique().shape[0]

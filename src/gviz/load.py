from typing import List

import pandas as pd
from pathlib import Path
import warnings

from .common import *

"""Represent the loader to load records as dataframe from the data file as required.

Below is a excerpt of a record sheet  (where the first row cell are headers):

date|machine|name|weight_0|handle_0|reps_0|xhstd_0|weight_1|handle_1|reps_1|xhstd_1|weight_2|handle_2|reps_2|xhstd_2|...
22/11/2023|shoulder press|seated shoulder press|2.5|back|12.0|0.0|5.0|front|9.0|1.0|5.0|back|7.0|1.0|...
22/11/2023|chest press|seated chest press|10.0|NaN|12.0|0.0|17.5|NaN|12.0|0.0|17.5|NaN|12.0|0.0|...
22/11/2023|pectoral machine|pectoral fold|20.0|NaN|13.0|1.0|20.0|NaN|5.0|1.0|17.5|NaN|11.0|1.0|...
"""


class Loader:
    def __init__(self, data_file: str, sheet_names=None,
                 col_date=COL_DATE, date_format='%d%m%Y') -> None:
        """
        Args:
            data_file: The path to the date file (e.g. an Excel file)
            sheet_names: Sheets names to extract.
                Default as None, all sheets starting with "records" will be extracted.
            col_date: Column name of date. Default as `COL_DATE`
            date_format: String of date format, Default as '%d%m%Y'.
        """
        data_file = Path(data_file)
        assert data_file.exists(), f'The given path {data_file} does NOT exist'
        assert data_file.is_file(), f'The given path {data_file} is NOT a path'
        assert data_file.suffix == '.xlsx', f'Unsupported format {data_file.suffix}'
        self._data_file = data_file
        self._col_date = col_date

        if sheet_names is None:
            xls = pd.ExcelFile(self._data_file)
            sheet_names = [sheet_name for sheet_name in xls.sheet_names if sheet_name.startswith("records")]
        elif isinstance(sheet_names, str):
            sheet_names = [sheet_names]
        assert isinstance(sheet_names, list), 'Arg sheet_names should be a string or a list of strings.'

        self._df = None
        # Suppress the warning
        warnings.filterwarnings("ignore", category=UserWarning)
        dfs = []
        for sheet_name in sheet_names:
            dfs.append(pd.read_excel(self._data_file, sheet_name=sheet_name, date_format=date_format))
        self._df = pd.concat(dfs, ignore_index=True)
        self._df = self._df.dropna(subset=[COL_DATE])
        # Restore the warning
        warnings.filterwarnings("default", category=UserWarning)

        self._max_date = self._df[self._col_date].max()
        self._min_date = self._df[self._col_date].min()

    def get_records(self, start_date: str = None, end_date: str = None, gyms: List = None) -> pd.DataFrame:
        """Get records (within the given range of time).
        Note that the retrieved records are not in any order.

        Args:
            start_date (str, optional): Inclusive. Defaults to the min date in all records.
                Prefer format "yyyy-mm-dd".
            end_date (str, optional): Inclusive. Defaults to the max date in all records.
                Prefer format "yyyy-mm-dd".
            gyms (List, optional): A list of gym names to filtered out. Default as None (all records are extracted).

        Returns:
            pd.DataFrame: The records being filtered out.
        """
        start_date = self._min_date if start_date is None else pd.Timestamp(start_date)
        end_date = self._max_date if end_date is None else pd.Timestamp(end_date)
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date, dayfirst=True)
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date, dayfirst=True)

        # Filter records within the specified date range
        filtered_df = self._df.loc[
            (self._df[self._col_date] >= start_date) & (self._df[self._col_date] <= end_date)]
        if gyms is not None:
            filtered_df = filtered_df[filtered_df[COL_GYM].isin(gyms)]

        return filtered_df

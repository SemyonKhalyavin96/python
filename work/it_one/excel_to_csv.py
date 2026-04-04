from typing import Union, List
from pathlib import Path
import os
import csv
import pandas as pd


def excel_to_csv(src_folder: Union[Path, str], file: str, dest_folder: Union[Path, str], sep: str,
                 file_by_sheet: bool = False, sheet_col_name: str = None, quoting: int = csv.QUOTE_NONE):
    """
    Процедура преобразования Excel-файла в CSV-формат
    Args:
        src_folder: папка, в которой находится Excel-файл
        file: название Excel-файла
        dest_folder: папка-назначение для CSV-файла
        sep: разделитель для CSV-файла
        file_by_sheet: флаг разбиения Excel-файла на CSV по листам, по умолчанию False
        sheet_col_name: поле для названия листа, по умолчанию None
        quoting: optional constant from csv module
    """
    pd.set_option('future.no_silent_downcasting', True)
    filename, file_extension = os.path.splitext(file)
    xls = pd.ExcelFile(f'{str(src_folder)}/{file}')
    sum_df = pd.read_excel(xls, xls.sheet_names[0], dtype=object)
    sum_df.columns = sum_df.columns.map(lambda x: x.replace('\r', '').replace('\n', ''))
    if sheet_col_name:
        sum_df[sheet_col_name] = pd.Series(dtype=object)
    sum_df = sum_df.iloc[0:0]

    for sheet in xls.sheet_names:
        data_xls = pd.read_excel(xls, sheet, dtype=object)
        if sheet_col_name:
            data_xls[sheet_col_name] = sheet
        data_xls.columns = data_xls.columns.map(lambda x: x.replace('\r', '').replace('\n', ''))
        if file_by_sheet:
            data_xls = data_xls.replace(r'\n', '', regex=True).infer_objects(copy=False)
            data_xls.to_csv(f'{str(dest_folder)}/{filename}_{sheet}.csv', sep=sep, encoding='utf-8',
                            index=False, quoting=quoting)
            continue
        sum_df = pd.concat([sum_df, data_xls], ignore_index=True)

    if not file_by_sheet:
        sum_df = sum_df.replace(r'\n', '', regex=True).infer_objects(copy=False)
        sum_df.to_csv(f'{str(dest_folder)}/{filename}.csv', sep=sep, encoding='utf-8', index=False,
                      quoting=quoting)


excel_to_csv(src_folder='C:\\Users\\SKhalyavin\\PycharmProjects\\test\\data\\excel', file='Шаблон БФ отчет.xlsx',
             dest_folder='C:\\Users\\SKhalyavin\\PycharmProjects\\test\\data\\csv', sep=';', sheet_col_name='test')
# excel_to_csv(src_folder='C:\\Users\\SKhalyavin\\PycharmProjects\\test\\data\\excel', file='Шаблон БФ отчет.xls',
#              dest_folder='C:\\Users\\SKhalyavin\\PycharmProjects\\test\\data\\csv', sep=';', sheet_col_name='test')
# excel_to_csv(src_folder='C:\\Users\\SKhalyavin\\PycharmProjects\\test\\data\\excel', file='Шаблон БФ отчет_1.xls',
#              dest_folder='C:\\Users\\SKhalyavin\\PycharmProjects\\test\\data\\csv', sep=';', sheet_col_name='test')

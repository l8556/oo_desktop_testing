# -*- coding: utf-8 -*-
import csv
from _csv import reader
from os.path import dirname, join, isfile
import pandas as pd

import config
from frameworks.host_control import FileUtils


class Report:

    def __init__(self):
        self._set_pandas_options()

    @staticmethod
    def _set_pandas_options():
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option("expand_frame_repr", False)


    def merge(self, reports: list, result_csv_path: str, delimiter='\t') -> "str | None":
        if reports:
            df = pd.concat([self.read(csv_, delimiter) for csv_ in reports if isfile(csv_)], ignore_index=True)
            df.to_csv(result_csv_path, index=False, sep=delimiter)
            return result_csv_path
        print('[green]|INFO| No files to merge')

    @staticmethod
    def write(file_path: str, mode: str, message: list, delimiter='\t', encoding='utf-8') -> None:
        FileUtils.create_dir(dirname(file_path), stdout=False)
        with open(file_path, mode, newline='', encoding=encoding) as csv_file:
            writer = csv.writer(csv_file, delimiter=delimiter)
            writer.writerow(message)

    @staticmethod
    def read(csv_file: str, delimiter: str = "\t") -> list:
        with open(csv_file, 'r') as csvfile:
            return [row for row in reader(csvfile, delimiter=delimiter)]

    @staticmethod
    def save_csv(df, csv_path: str, delimiter="\t") -> str:
        df.to_csv(csv_path, index=False, sep=delimiter)
        return csv_path
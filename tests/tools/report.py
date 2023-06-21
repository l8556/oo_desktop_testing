# -*- coding: utf-8 -*-
import csv
from _csv import reader
from os.path import dirname

from frameworks.host_control import FileUtils


class Report:

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
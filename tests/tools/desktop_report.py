# -*- coding: utf-8 -*-
from os.path import dirname

from frameworks.host_control import FileUtils
from tests.tools.report import Report


class DesktopReport:
    def __init__(self, report_path: str):
        self.path = report_path
        self.dir = dirname(self.path)
        FileUtils.create_dir(self.dir, stdout=False)
        self._writer(self.path, 'w', [ 'Os', 'Version', 'Package_name', 'Exit_code'])

    def write(self, package_name: str, version: str, os: str, exit_code: str):
        self._writer(self.path, 'a', [package_name, version, os, exit_code])

    @staticmethod
    def _writer(file_path: str, mode: str, message: list, delimiter='\t', encoding='utf-8'):
        Report.write(file_path, mode, message, delimiter, encoding)

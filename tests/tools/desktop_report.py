# -*- coding: utf-8 -*-
from os.path import join

import config
from frameworks.host_control import FileUtils
from tests.tools.report import Report


class DesktopReport:
    def __init__(self, reports_dir: str, version: str):
        self.report_dir = reports_dir
        self.path = join(self.report_dir, f"{version}_desktop_report.csv")
        FileUtils.create_dir(self.report_dir, stdout=False)
        self._writer(self.path, 'w', ['Package_name', 'Version', 'Os', 'Exit_code'])

    def write(self, package_name: str, version: str, os: str, exit_code: str):
        self._writer(self.path, 'a', [package_name, version, os, exit_code])

    @staticmethod
    def _writer(file_path: str, mode: str, message: list, delimiter='\t', encoding='utf-8'):
        Report.write(file_path, mode, message, delimiter, encoding)

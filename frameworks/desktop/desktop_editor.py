# -*- coding: utf-8 -*-
import os
from os.path import join, dirname
from subprocess import Popen, PIPE
from frameworks.host_control import HostInfo, FileUtils


class DesktopEditor:
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.os = HostInfo().os
        self.tmp_dir = join(os.getcwd(), "tmp")
        self.log_file = join(self.tmp_dir, "desktop.log")
        self.create_log_file()
        self.debug_command = f'--ascdesktop-log-file={"stdout" if HostInfo().os != "windows" else self.log_file}'

    def open(self, file_path: str = None):
        process = Popen(
            f"{self._generate_running_command()} "
            f"{self.debug_command if self.debug_mode else ''} "
            f"{file_path if file_path else ''}".strip(),
            stdout=PIPE, stderr=PIPE, shell=True
        )
        return process

    def close(self):
        # call('killall DesktopEditors', shell=True)
        ...

    def read_log(self, wait_msg):
        for line in FileUtils.file_reader(self.log_file).split('\n'):
            print(line) if line else ...
            if wait_msg == line.strip():
                self.create_log_file()
                return

    def create_log_file(self):
        FileUtils.create_dir(dirname(self.log_file), stdout=False)
        FileUtils.file_writer(self.log_file, '', mode='w')

    def _generate_running_command(self):
        if self.os == 'linux':
            return 'onlyoffice-desktopeditors'
        elif self.os == 'mac':
            return '/Applications/ONLYOFFICE.app/Contents/MacOS/ONLYOFFICE'
        elif self.os == 'windows':
            ...
        else:
            raise print(f"[red]|ERROR| Can't verify OS")

# -*- coding: utf-8 -*-
import os
import re
from os.path import join, dirname, isfile, basename
from subprocess import Popen, PIPE
from frameworks.host_control import HostInfo, FileUtils
from rich import print


class DesktopEditor:
    def __init__(self, debug_mode: bool = False, custom_config: str = None, lic_file: str = None):
        self.lic_file_path = lic_file
        self.custom_config = custom_config
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

    def version(self) -> "str | None":
        version = re.findall(r"\d+\.\d+\.\d+\.\d+", FileUtils.output_cmd(f'{self._generate_running_command()} --version'))
        return version[0] if version else None

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

    def set_license(self):
        if self.custom_config:
            lic_file = FileUtils.read_json(self.custom_config).get(f"lic_path_{HostInfo().os}")
            if lic_file and isfile(self.lic_file_path):
                FileUtils.copy(self.lic_file_path, join(lic_file, basename(self.lic_file_path)))
                print(f"[green]|INFO| Desktop activated")

    def _generate_running_command(self):
        if self.os == 'linux':
            if self.custom_config:
                return FileUtils.read_json(self.custom_config)['linux_run_command']
            return 'onlyoffice-desktopeditors'
        elif self.os == 'mac':
            if self.custom_config:
                return FileUtils.read_json(self.custom_config)['mac_run_command']
            return '/Applications/ONLYOFFICE.app/Contents/MacOS/ONLYOFFICE'
        elif self.os == 'windows':
            if self.custom_config:
                return FileUtils.read_json(self.custom_config)['windows_run_command']
        else:
            raise print(f"[red]|ERROR| Can't verify OS")

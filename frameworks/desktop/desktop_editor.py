# -*- coding: utf-8 -*-
import re
from os.path import join, dirname, isfile, basename, realpath
from subprocess import Popen, PIPE
from frameworks.host_control import HostInfo, FileUtils
from rich import print

from .package import Package
from .data import Data


class DesktopEditor:
    def __init__(self, data: Data):
        self.lic_file_path = data.lic_file
        self.debug_mode = data.debug_mode
        self.config = self._get_config(data.custom_config_path)
        self.package = Package(data)
        self.os = HostInfo().os
        self.tmp_dir = data.tmp_dir
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
        # Todo
        # call('killall DesktopEditors', shell=True) -> segmentation fault in stdout
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
        license_dir = self.config.get(f"lic_dir_{HostInfo().os}")
        if license_dir:
            if license_dir and isfile(self.lic_file_path):
                FileUtils.create_dir(license_dir, stdout=False)
                FileUtils.copy(self.lic_file_path, join(license_dir, basename(self.lic_file_path)))
                return print(f"[green]|INFO| Desktop activated")
        print("[green]|INFO| Free license")

    def _generate_running_command(self):
        run_cmd = self.config.get(f'{HostInfo().os}_run_command')
        if run_cmd:
            return run_cmd
        raise ValueError(f"[red]|ERROR| Can't get running command, key: {HostInfo().os}_run_command")

    @staticmethod
    def _get_config(path):
        config_path = path if path and isfile(path) else join(dirname(realpath(__file__)), 'desktop_config.json')
        return FileUtils.read_json(config_path)

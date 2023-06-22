# -*- coding: utf-8 -*-
from subprocess import Popen
from frameworks.host_control import HostInfo

class DesktopEditor:
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.os = HostInfo().os

    def open(self, file_path: str = None):
        Popen(
            f"{self._generate_running_command()} "
            f"{'--ascdesktop-support-debug-info' if self.debug_mode else ''} "
            f"{file_path if file_path else ''}".strip(),
            shell=True
        )

    def close(self):
        # call('killall DesktopEditors', shell=True)
        ...

    def _generate_running_command(self):
        if self.os == 'linux':
            return 'onlyoffice-desktopeditors'
        elif self.os == 'mac':
            return '/Applications/ONLYOFFICE.app/Contents/MacOS/ONLYOFFICE'
        elif self.os == 'windows':
            ...
        else:
            raise print(f"[red]|ERROR| Can't verify OS")

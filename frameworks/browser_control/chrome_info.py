# -*- coding: utf-8 -*-
import re

from frameworks.host_control import HostInfo, FileUtils
from frameworks.decorators import singleton

@singleton
class ChromeInfo:
    def __init__(self):
        self._os = HostInfo().os
        self._version = self._get_version()

    @property
    def version(self):
        if self._version:
            return self._version
        print(f"[bold red]|WARNING| Can't get Chrome version.")

    def _get_version(self) -> "str | None":
        command = self._get_version_command()
        return self._find_version(command) if command else None

    def _get_version_command(self) -> "str | None":
            if self._os == 'windows':
                return "powershell Get-ItemProperty -Path " \
                    "'HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Google Chrome\'" \
                    " -ErrorAction SilentlyContinue | Select-Object -ExpandProperty DisplayVersion"
            elif self._os == 'linux':
                return 'google-chrome --version'
            elif self._os == 'mac':
                return '"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version'
            else:
                return print(f"[red]|WARNING| Error defining os: {self._os}")

    @staticmethod
    def _find_version(command: str) -> "str | None":
        version = re.findall(r"\d+\.\d+\.\d+\.\d+", FileUtils.output_cmd(command))
        return version[0].strip() if version else print("[bold red] Chrome version not found.")

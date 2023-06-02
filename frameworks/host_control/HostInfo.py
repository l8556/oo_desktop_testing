# -*- coding: utf-8 -*-
from platform import system, machine
from rich import print

from . import FileUtils
from ..decorators.decorators import singleton


@singleton
class HostInfo:
    def __init__(self):
        self.os = system().lower()
        self.__arch = machine().lower()
        self._distributive_name = None
        self._distributive_version = None

    @property
    def distributive_name(self) -> str | None:
        if self.os == 'linux':
            if self._distributive_name:
                return self._distributive_name
            raise print(f"[bold red]|ERROR| Can't get distribution name")
        print(f"[red]|WARNING| Distribution name for linux only ")

    @property
    def distributive_version(self) -> str | None:
        if self.os == 'linux':
            if self._distributive_version:
                return self._distributive_version
            raise print(f"[bold red]|ERROR| Can't get distribution version")
        print(f"[red]|WARNING| Distribution version for linux only ")

    @property
    def os(self):
        return self.__os

    @property
    def arch(self):
        return self.__arch

    def _get_distributive_info(self):
        info = FileUtils.output_cmd("lsb_release -a")
        self._distributive_name = FileUtils.find_in_line_by_key(info, key='Distributor ID').strip()
        self._distributive_version = FileUtils.find_in_line_by_key(info, key='Release').strip()

    @os.setter
    def os(self, value):
        if value == 'linux':
            self._get_distributive()
            self.__os = 'linux'
        elif value == 'darwin':
            self.__os = 'mac'
        elif value == 'windows':
            self.__os = 'windows'
        else:
            print(f"[bold red]|WARNING| Error defining os: {value}")

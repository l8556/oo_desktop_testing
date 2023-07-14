# -*- coding: utf-8 -*-
from os.path import isfile, join, dirname, realpath
from frameworks.host_control import HostInfo, FileUtils
from frameworks.desktop.handlers.VersionHandler import VersionHandler
from ..data import Data

class UrlGenerator:
    def __init__(self, data: Data):
        self.version_handler = VersionHandler(data.version)
        self.host_name = HostInfo().name().lower()
        self.host_version = HostInfo().version
        self.version = self.version_handler.version
        self.major_version = self.version_handler.major_version
        self.minor_version = self.version_handler.minor_version
        self.build = self.version_handler.build
        self.config = self._get_config(data.custom_config_path)
        self.cef103_system: list = self.config.get('cef103_system') # f"{HostInfo().name().lower()} {HostInfo().version}"
        print(f"[green]|INFO| Host Information: {self.host_name} {HostInfo().version}")

    @property
    def host(self):
        return self._read_config_by_key("host")

    @property
    def os_family(self):
        for os, distributions in self._read_config_by_key('os_family').items():
            if self.host_name in distributions:
                return os
        raise print(f"[red]|ERROR| Can't verify _os os_family for download desktop package.\n"
                    f"distributive: {self.host_name}\n"
                    f"version: {self.host_version}")
    @property
    def url(self):
        return f"{self.host}/{self._os}/{self.os_family}/{self.package_name}".strip()

    @property
    def package_name(self):
        if f"{self.host_name} {self.host_version}" in self.cef103_system:
            return self._read_package_name(self.os_family, 'cef103')
        return self._read_package_name(self.os_family, 'cef107')

    @property
    def _url_version(self):
        if self._os == 'windows':
            return self.version
        return f"{self.major_version}.{self.minor_version}-{self.build}"

    def _read_config_by_key(self, key: str):
        config = self.config.get(key)
        if config:
            return config
        raise ValueError(f"[red]|ERROR|UrlGenerator| Can't get config by key: {key}")

    @property
    def _os(self):
        if HostInfo().os == 'windows':
            return 'win'
        return HostInfo().os

    def _read_package_name(self, os_family: str, key: str):
        try:
            return self.config['package_name'][os_family][key].replace("[version]", self._url_version)
        except KeyError:
            print(f"[red]|WARNING| Can't get package name by key: {key}, os_family: {self.os_family}")

    @staticmethod
    def _get_config(path: str):
        config_path = path if path and isfile(path) else join(dirname(realpath(__file__)), 'url_config.json')
        return FileUtils.read_json(config_path)

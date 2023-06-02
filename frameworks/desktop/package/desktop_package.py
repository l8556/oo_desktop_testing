# -*- coding: utf-8 -*-
import config
from .url_generator import UrlGenerator
from rich import print

from frameworks.host_control import FileUtils, HostInfo
from frameworks.decorators.decorators import highlighter
from frameworks.StaticData import StaticData
from os.path import basename



class DesktopPackage:
    def __init__(self,  version: str = config.version):
        self.os = HostInfo().os
        self.url = UrlGenerator(config.version).url
        self.version = version
        self.tmp_dir = StaticData.tmp_dir

    @highlighter(color='green')
    def get(self):
        if not FileUtils.get_headers(self.url):
            return
        print(f"[green]|INFO| Downloading Desktop package\nVersion: {self.version}\nOS: {self.os}\nURL: {self.url}")
        FileUtils.download_file(self.url, self.tmp_dir)
        return basename(self.url)

import re
import time
from subprocess import call


from .url_generator import UrlGenerator
from rich import print

from frameworks.host_control import FileUtils, HostInfo
from frameworks.decorators.decorators import highlighter
from os.path import join, isfile, basename, getsize


from ..desktop_data import  DesktopData


class Package:
    def __init__(self, config_data: DesktopData, sudo_password: str = None):
        self.pwd = sudo_password
        self.generator = UrlGenerator(config_data.version)
        self.os = HostInfo().name(pretty=True)
        self.url =  self.generator.url
        self.name = self.generator.package_name
        self.version = config_data.version
        self.download_dir = config_data.cache_dir if config_data.cache_dir else config_data.tmp_dir
        self.package_path = join(self.download_dir, basename(self.url))
        FileUtils.create_dir(self.download_dir, stdout=False)

    def get(self) -> "bool | None":
        if self.is_installed():
            return
        headers = FileUtils.get_headers(self.url)
        if self.check_package_exists(headers):
            print(f"[green]|INFO| OnlyOffice Package {basename(self.package_path)} already exists")
        else:
            self.download() if headers else print(f"[red]|WARNING| Package does not exist on aws")
        self.install()

    def is_installed(self) -> bool:
        if self.get_version() == self.version:
            print(f'[green]|INFO| OnlyOffice Desktop version: {self.version} already installed[/]')
            return True
        return False

    @staticmethod
    def _correct_version(version):
        if len([i for i in version.split('.') if i]) == 4:
            return True
        print(f"[red]|WARNING| The version is not correct: {version}")
        return False


    @staticmethod
    def get_version() -> "str | None":
        version = re.findall(r"\d+\.\d+\.\d+\.\d+", FileUtils.output_cmd('onlyoffice-desktopeditors --version'))
        return version[0] if version else print(f"[bold red]|WARNING| Unable to get an installed version of OnlyOffice Desktop")

    @highlighter(color='green')
    def download(self) -> None:
        print(f"[green]|INFO| Downloading Desktop package\nVersion: {self.version}\nOS: {self.os}\nURL: {self.url}")
        FileUtils.download_file(self.url, self.download_dir)

    def check_package_exists(self, headers: "dict | None" = None) -> bool:
        if headers and isfile(self.package_path):
            return int(getsize(self.package_path)) == int(headers['Content-Length'])
        elif isfile(self.package_path):
            return True
        return False

    def install(self) -> None:
        if isfile(self.package_path):
            print(f"[green]|INFO| Installing OnlyOffice Desktop version: {self.version}")
            call(self._get_install_command(), shell=True)
        else:
            print(f"[red]|ERROR|Package not exists.")


    def _get_install_command(self):
        if HostInfo().name().lower() in ['debian', 'ubuntu']:
            return f'sudo dpkg -i {join(self.download_dir, self.name)}'
        elif HostInfo().name().lower() in ['centos', 'redos']:
            return f'sudo dnf localinstall {join(self.download_dir, self.name)} -y'

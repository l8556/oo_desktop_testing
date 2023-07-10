import re
from subprocess import call, getoutput

from .Portal import Portal
from rich import print

from frameworks.host_control import FileUtils, HostInfo
from frameworks.decorators.decorators import highlighter
from os.path import join, isfile, basename, getsize

from ..desktop_data import  DesktopData


class Package:
    def __init__(self, package_portal: Portal, config_data: DesktopData):
        self.package_portal = package_portal
        self.os = HostInfo().name(pretty=True)
        self.url =  self.package_portal.url
        self.name: str = self.package_portal.package_name
        self.version = config_data.version
        self.download_dir = config_data.cache_dir if config_data.cache_dir else config_data.tmp_dir
        self.package_path = join(self.download_dir, self.name)
        FileUtils.create_dir(self.download_dir, stdout=False)

    def get(self) -> "None":
        headers = FileUtils.get_headers(self.url)
        if self.check_package_exists(headers):
            print(f"[green]|INFO| OnlyOffice Package {basename(self.package_path)} already exists")
        else:
            self.download() if headers else print(f"[red]|WARNING| Package does not exist on aws")
        self.install()

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

    @staticmethod
    def _unlock_dpkg():
        commands = [
            "sudo rm /var/lib/apt/lists/lock",
            "sudo rm /var/cache/apt/archives/lock",
            "sudo rm /var/lib/dpkg/lock",
            "sudo rm /var/lib/dpkg/lock-frontend"
        ]
        for cmd in commands:
            FileUtils.run_command(cmd)

    def _get_install_command(self):
        host_name = HostInfo().name().lower()
        if host_name in ['debian', 'ubuntu', "linuxmint", 'pop', 'astra']:
            self._unlock_dpkg()
            return f'sudo dpkg -i {self.package_path}'
        elif host_name in ['redos', 'fedora']:
            return f'sudo dnf localinstall {self.package_path} -y'
        elif host_name in ['altlinux', 'opensuse', 'centos', 'rosa']:
            return f'sudo rpm -i {self.package_path}'
        else:
            raise print(f"[red]|ERROR| Unable to generate a command to install the desktop package.\n"
                        f"os family: {HostInfo().name().lower()}\n"
                        f"version: {HostInfo().version}")

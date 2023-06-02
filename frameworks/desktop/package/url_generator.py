# -*- coding: utf-8 -*-
from frameworks.host_control import FileUtils, HostInfo
from ..handlers.VersionHandler import VersionHandler

class UrlGenerator:

    def __init__(self, version: str):
        self.version_handler= VersionHandler(version)
        self.version = self.version_handler.version
        self.host = 'https://s3.eu-west-1.amazonaws.com/repo-doc-onlyoffice-com/desktop'
        self.major_version = self.version_handler.major_version
        self.minor_version = self.version_handler.minor_version
        self.build = self.version_handler.build
        self.distributive = self._verify_distributive()



    @property
    def url(self):
        # TODO linux/debian/onlyoffice-desktopeditors_7.4.0-113_amd64.deb"
        return f"{self.host}/{self._os}/{self.distributive}/{self.package_name}"


    @property
    def package_name(self):
            # deb packages
            if self.distributive == 'debian':
                if self.distributive_version in ['22.04']:
                    return f"onlyoffice-desktopeditors_{self._url_version}-cef107_amd64.deb"
                return f"onlyoffice-desktopeditors_{self._url_version}_amd64.deb"

            # CentOS rpm packages
            elif self.distributive == 'rhel':
                ...

            # SUSE Linux rpm packages
            elif self.distributive == 'suse':
                ...

            # Portable
            elif self.distributive == 'generic':
                ...

    @staticmethod
    def _verify_distributive():
        distributive = FileUtils.find_in_line_by_key(FileUtils.output_cmd("lsb_release -a"), key='Distributor ID').strip()
        if distributive in ['Ubuntu', 'Debian']:
            return 'debian'

    @staticmethod
    def distributive_version():
        return FileUtils.find_in_line_by_key(FileUtils.output_cmd("lsb_release -a"), key='Release').strip()

    @property
    def _url_version(self):
        if self._os == 'windows':
            return self.version
        return f"{self.major_version}.{self.minor_version}-{self.build}"


    @property
    def _os(self):
        if HostInfo().os == 'linux':
            return 'linux'
        elif HostInfo().os == 'mac':
            return 'mac'
        elif HostInfo().os == 'windows':
            return 'windows'

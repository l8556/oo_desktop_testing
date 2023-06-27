# -*- coding: utf-8 -*-
from frameworks.host_control import HostInfo
from ..handlers.VersionHandler import VersionHandler

class UrlGenerator:

    def __init__(self, version: str):
        self.version_handler = VersionHandler(version)
        self.version = self.version_handler.version
        self.major_version = self.version_handler.major_version
        self.minor_version = self.version_handler.minor_version
        self.build = self.version_handler.build
        self.host = 'https://s3.eu-west-1.amazonaws.com/repo-doc-onlyoffice-com/desktop'


    @property
    def distributive(self):
        if HostInfo().name().lower() in ['debian', 'ubuntu']:
            return 'debian'
        elif HostInfo().name().lower() in ['centos', 'redos', 'altlinux']:
            return 'rhel'
        elif HostInfo().name().lower() in ['opensuse']:
            return 'suse'
        else:
            raise print(f"[red]|ERROR| Can't verify os distributive for download desktop package.\n"
                        f"distributive: {HostInfo().name().lower()}\n"
                        f"version: {HostInfo().version}")

    @property
    def url(self):
        return f"{self.host}/{self._os}/{self.distributive}/{self.package_name}".strip()

    @property
    def package_name(self):
            # deb packages
            if self.distributive in ['debian']:
                if HostInfo().name().lower() == 'ubuntu' and HostInfo().version in ['22.04']:
                    return f"onlyoffice-desktopeditors_{self._url_version}~cef107_amd64.deb"
                return f"onlyoffice-desktopeditors_{self._url_version}_amd64.deb"

            # CentOS rpm packages
            elif self.distributive in ['rhel']:
                if HostInfo().version in ['9', '7.3.2', '10.1']:
                    return f'onlyoffice-desktopeditors-{self._url_version}~cef107.el7.x86_64.rpm'
                return f'onlyoffice-desktopeditors-{self._url_version}.el7.x86_64.rpm'

            # SUSE Linux rpm packages
            elif self.distributive in ['suse']:
                if HostInfo().version in []:
                    return 'onlyoffice-desktopeditors-7.4.0-166.suse12.x86_64.rpm'
                return 'onlyoffice-desktopeditors-7.4.0-166~cef107.suse12.x86_64.rpm'

            # Portable
            elif self.distributive in ['generic']:
                ...


    @property
    def _url_version(self):
        if self._os == 'windows':
            return self.version
        return f"{self.major_version}.{self.minor_version}-{self.build}"


    @property
    def _os(self):
        return HostInfo().os

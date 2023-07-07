# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod


class Portal(ABC):
    @property
    @abstractmethod
    def host(self) -> str: ...

    @property
    @abstractmethod
    def os_family(self): ...

    @property
    @abstractmethod
    def url(self): ...

    @property
    @abstractmethod
    def package_name(self): ...

    @property
    @abstractmethod
    def _url_version(self): ...

# -*- coding: utf-8 -*-
from typing import NamedTuple

class DesktopData(NamedTuple):
    version: str
    tmp_dir: str
    cache_dir: str = None
    custom_config: str = None
    lic_file: str = None

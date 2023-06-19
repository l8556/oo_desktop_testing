# -*- coding: utf-8 -*-
from .FileUtils import FileUtils
from .host_info import HostInfo

if HostInfo().os == 'windows':
    from .windows_handler import Window
from ..host_info import HostInfo

if HostInfo().os == 'windows':
    from .windows import Window

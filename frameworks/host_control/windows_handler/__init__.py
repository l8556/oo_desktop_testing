from ..HostInfo import HostInfo

if HostInfo().os == 'windows':
    from .windows import Window

# -*- coding: utf-8 -*-
from dataclasses import dataclass
from os import getcwd
from os.path import join



@dataclass(frozen=True)
class StaticData:
    project_dir: str = getcwd()
    # tmp
    tmp_dir: str = join(project_dir, 'tmp')

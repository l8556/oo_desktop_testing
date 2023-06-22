# -*- coding: utf-8 -*-
from dataclasses import dataclass
from os import getcwd
from os.path import join
import config



@dataclass(frozen=True)
class StaticData:
    project_dir: str = getcwd()
    tmp_dir: str = join(project_dir, 'tmp')
    cache_dir: str = config.cache_dir if config.cache_dir else None
    reports_dir: str = join(project_dir, 'reports')
    img_template: str = join(project_dir, 'tests', 'assets', 'image_template')
    bad_files_dir: str = join(project_dir, 'tests', 'assets', 'bad_files')
    good_files_dir: str = join(project_dir, 'tests', 'assets', 'good_files')

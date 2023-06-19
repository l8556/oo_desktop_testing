# -*- coding: utf-8 -*-
from invoke import task

from tests.desktop_test import DesktopTest


@task
def desktop_test(c, version=None):
    DesktopTest(version=version).run()

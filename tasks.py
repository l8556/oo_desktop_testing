# -*- coding: utf-8 -*-
from invoke import task

from tests.desktop_test import DesktopTest


@task
def desktop_test(c, version=None, display=False, custom_config=None, telegram=False):
    DesktopTest(
        version=version,
        display_on=True if not display else False,
        custom_config=custom_config,
        telegram=telegram
    ).run()

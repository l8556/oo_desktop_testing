# -*- coding: utf-8 -*-
import os
from os.path import join

from invoke import task

from tests.desktop_test import DesktopTest


@task
def desktop_test(c, version=None, display=False, custom_config=None, telegram=False):
    DesktopTest(
        version=version,
        display_on=True if not display else False,
        custom_config=join(os.getcwd(), 'portal_config.json') if custom_config else None,
        telegram=telegram
    ).run()

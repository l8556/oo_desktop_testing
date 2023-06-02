# -*- coding: utf-8 -*-

from invoke import task

from frameworks.desktop.installer import Installer


@task
def desktop(c):
    # pwd = Prompt.ask('Please enter sudo password', password=True, default=None)
    # DesktopPackage().get()
    Installer().run()
    # FileUtils.delete(StaticData.TMP_DIR, all_from_folder=True, silence=True)
    # UrlGenerator('7.4.0.150').distributive_version()

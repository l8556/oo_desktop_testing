# -*- coding: utf-8 -*-
import re
from frameworks.desktop import Package, DesktopEditor, DesktopData, OnlyOfficePortal

import time
from frameworks.StaticData import StaticData

from os.path import join, basename
from frameworks.host_control import FileUtils, HostInfo
from frameworks.image_handler import Image
from rich import print
from rich.console import Console

from pyvirtualdisplay import Display

from frameworks.telegram import Telegram
from tests.tools.desktop_report import DesktopReport

console = Console()

class DesktopTest:
    def __init__(self, version: str, custom_config: str = None, display_on: bool = True, telegram: bool = False):
        self.custom_config = custom_config
        self.telegram_report = telegram
        self.version = version
        self.display_on = display_on
        self.portal_config = join(StaticData.project_dir, 'portal_config.json')
        self.package = self._package(version, custom_config)
        self._create_display()
        self.report = DesktopReport(StaticData.reports_dir, self.version)
        self.host_name = re.sub(r"[\s/]", "", HostInfo().name(pretty=True))
        self.desktop = DesktopEditor(debug_mode=True, custom_config=custom_config, lic_file=StaticData.lic_file_path)
        self.img_dir = StaticData.img_template
        self.bad_files = StaticData.bad_files_dir
        self.good_files = StaticData.good_files_dir

    def run(self):
        self._install_package()
        self.check_installed()
        self.desktop.set_license()
        self.wait_until_open(self.desktop.open(), '[DesktopEditors]: start page loaded')
        self.check_open_files()
        self._write_results(f'Passed')
        self.desktop.close()
        self.display.stop() if self.display_on else ...

    def _install_package(self):
        if self.version == self.desktop.version():
            print(f'[green]|INFO| OnlyOffice Desktop version: {self.version} already installed[/]')
            return
        self.package.get()

    def check_open_files(self):
        for file in FileUtils.get_paths(self.good_files):
            # Todo
            if self.custom_config and file.endswith('.docxf'):
                continue
            print(f"[green]|INFO| Test opening file: {basename(file)}")
            self.desktop.open(file)
            time.sleep(25) # TODO
            self.check_error_on_screen()
            Image.make_screenshot(f"{join(self.report.dir, f'{self.version}_{self.host_name}_{basename(file)}.png')}")

    def check_error_on_screen(self):
        for img in FileUtils.get_paths(join(self.img_dir, 'errors')):
            if Image.is_image_present(img):
                Image.make_screenshot(f"{join(self.report.dir, f'{self.version}_{self.host_name}_error_screen.png')}")
                self._write_results('ERROR')
                raise print(f"[red]|ERROR| An error has been detected.")

    def wait_until_open(self, process, wait_msg, timeout=30):
        start_time = time.time()
        with console.status('') as status:
            while time.time() - start_time < timeout:
                status.update(f'[green]|INFO| Wait until the editor opens')
                output = process.stdout.readline().decode().strip()
                if output:
                    console.print(f"[cyan]|INFO|{output}")
                    if wait_msg in output:
                        self.check_error_on_screen()
                        break
            else:
                self._write_results('NOT_OPENED')
                raise console.print("[red]|ERROR| Can't open editor ")
            Image.make_screenshot(f"{join(self.report.dir, f'{self.version}_{self.host_name}_open_editor.png')}")

    def check_installed(self):
        installed_version = self.desktop.version()
        if self.version != installed_version:
            self._write_results('NOT_INSTALLED')
            raise print(
                f"[bold red]|ERROR| OnlyOffice Desktop not installed. "
                f"Current version: {installed_version}"
            )

    def _write_results(self, results):
        self.report.write(HostInfo().name(pretty=True), self.version, self.package.name, results)
        if self.telegram_report:
            self._send_report_to_telegram(results)

    def _send_report_to_telegram(self, results: str):
        pkg_name = re.sub(r"[\s/_]", "", self.package.name)
        Telegram().send_media_group(
            document_paths=self._get_report_files(),
            caption=f'Os: `{HostInfo().name(pretty=True)}`\n'
                    f'Version: `{self.version}`\n'
                    f'Package: `{pkg_name}`\n'
                    f'Result: `{results if results == "Passed" else "Error"}`'
        )

    def _get_report_files(self):
        return FileUtils.get_paths(self.report.dir, extension='.png')

    @staticmethod
    def _correct_version(version):
        if len([i for i in version.split('.') if i]) == 4:
            return True
        print(f"[red]|WARNING| The version is not correct: {version}")
        return False

    @staticmethod
    def _package(version: str, custom_config: str) -> Package:
        return Package(
            OnlyOfficePortal(version, custom_config),
            DesktopData(
                tmp_dir=StaticData.tmp_dir,
                version=version,
                cache_dir=StaticData.cache_dir,
                custom_config=custom_config
            )
        )

    def _create_display(self):
        if self.display_on:
            self.display = Display(visible=0, size=(1920, 1080))
            self.display.start()
        else:
            print("[red]|INFO| Test running without virtual display")

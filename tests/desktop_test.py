# -*- coding: utf-8 -*-
import re
from frameworks.desktop import DesktopEditor, DesktopData

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
    def __init__(
            self,
            version: str,
            custom_config: str = None,
            display_on: bool = True,
            telegram: bool = False,
            license_file_path=None
    ):
        self.config = FileUtils.read_json(custom_config) if custom_config else StaticData.config
        self.telegram_report = telegram
        self.version = version
        self.display_on = display_on
        self._create_display()
        self.report = DesktopReport(self._report_path())
        self.host_name = re.sub(r"[\s/]", "", HostInfo().name(pretty=True))
        self.img_dir = StaticData.img_template
        self.bad_files = StaticData.bad_files_dir
        self.good_files = StaticData.good_files_dir
        self.desktop = self._desktop(custom_config, license_file_path)

    def _report_path(self):
        title = self.config.get('title')
        return join(StaticData.reports_dir, title, self.version, f"{self.version}_{title}_report.csv")

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
        self.desktop.package.get()

    def check_open_files(self):
        for file in FileUtils.get_paths(self.good_files):
            if basename(file) in self.config.get('exception_files') if self.config.get('exception_files') else []:
                print(f"['cyan']|INFO| File `{basename(file)}` skipped to open.")
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
                        print(f"[green]|INFO| Opened.")
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
        self.report.write(HostInfo().name(pretty=True), self.version, self.desktop.package.name, results)
        if self.telegram_report:
            self._send_report_to_telegram(results)

    def _send_report_to_telegram(self, results: str):
        pkg_name = re.sub(r"[\s/_]", "", self.desktop.package.name)
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

    def _create_display(self):
        if self.display_on:
            self.display = Display(visible=0, size=(1920, 1080))
            self.display.start()
        else:
            print("[red]|INFO| Test running without virtual display")

    def _desktop(self, custom_config: str, license_file_path: str):
        return DesktopEditor(
            DesktopData(
                version=self.version,
                tmp_dir=StaticData.tmp_dir,
                debug_mode=True,
                custom_config_path=custom_config,
                lic_file=license_file_path if license_file_path else StaticData.lic_file_path,
                cache_dir=StaticData.cache_dir
            )
        )

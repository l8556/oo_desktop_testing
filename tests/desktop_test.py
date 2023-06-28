# -*- coding: utf-8 -*-
import re
from dataclasses import dataclass
from frameworks.browser_control import Chrome
from frameworks.decorators.decorators import retry
from frameworks.desktop import Package, DesktopEditor, DesktopData

import time
from frameworks.StaticData import StaticData

from os.path import join, dirname, realpath, basename
from frameworks.host_control import FileUtils, HostInfo, Window
from frameworks.image_handler import Image
from rich import print

from selenium.webdriver.chrome.options import Options
from pyvirtualdisplay import Display

from frameworks.telegram import Telegram
from tests.tools.desktop_report import DesktopReport


@dataclass(frozen=True)
class XPath:
    hello_document: str = '//*[@id="items"]/p/a/div'

class DesktopTest:
    def __init__(self, version: str, sudo_password: str = None, display_on: bool = True):
        self.display_on = display_on
        self.version = version
        self.report = DesktopReport(StaticData.reports_dir, self.version)
        self.host_name = re.sub(r"[\s/]", "", HostInfo().name(pretty=True))
        self.package = Package(DesktopData(tmp_dir=StaticData.tmp_dir, version=self.version, cache_dir=StaticData.cache_dir), sudo_password=sudo_password)
        self.desktop = DesktopEditor(debug_mode=True)
        if self.display_on:
            self.display = Display(visible=0, size=(1920, 1080))
            self.display.start()
        self.exceptions: list = FileUtils.read_json(join(dirname(realpath(__file__)), 'assets', 'console_exceptions.json'))['console_exceptions']
        self.window = Window()
        self.window_id = None
        self.img_dir = StaticData.img_template
        self.bad_files = StaticData.bad_files_dir
        self.good_files = StaticData.good_files_dir

    @staticmethod
    def _chrome_options():
        chrome_options = Options()
        return chrome_options

    def run(self):
        self.package.get()
        self.check_installed()
        self.desktop.open()
        self.check_errors()
        self.check_open_files()
        self._write_results(f'Passed')
        self.desktop.close()
        if self.display_on:
            self.display.stop()

    def check_open_files(self):
        for file in FileUtils.get_paths(self.good_files):
            print(f"[green]|INFO| Test opening file: {basename(file)}")
            self.desktop.open(file)
            time.sleep(20) # TODO
            self.check_error_on_screen()
            Image.make_screenshot(f"{join(self.report.dir, f'{self.version}_{self.host_name}_{basename(file)}.png')}")
            # self.check_js_console()

    def check_errors(self):
        self.check_open_editor_window()
        self.check_error_on_screen()
        self.check_js_console()

    def check_error_on_screen(self):
        for img in FileUtils.get_paths(join(self.img_dir, 'errors')):
            if Image.is_image_present(img):
                Image.make_screenshot(f"{join(self.report.dir, f'{self.version}_{self.host_name}_error_screen.png')}")
                self._write_results('ERROR_ON_SCREEN')
                raise print(f"[red]|ERROR| Error on image.")

    def check_open_editor_window(self):
        self.window_id = self.window.wait_until_open(('DesktopEditors', 'ONLYOFFICE Desktop Editors'))
        time.sleep(8) # TODO
        if not self.window.get_hwnd(('DesktopEditors', 'ONLYOFFICE Desktop Editors')):
            Image.make_screenshot(f"{join(self.report.dir, f'{self.version}_{self.host_name}_open_editor.png')}")
            self._write_results(f"NotOpened")
            raise
        Image.make_screenshot(f"{join(self.report.dir, f'{self.version}_{self.host_name}_open_editor.png')}")

    def check_js_console(self):
        chrome = Chrome(chrome_options=self._chrome_options())
        self._connection_debug_mode(chrome)
        errors = self._check_console_log(chrome)
        chrome.make_screenshot(f"{join(self.report.dir, f'{self.version}_{self.host_name}_browser_screen.png')}")
        if errors:
            self._write_results(f'console_errors: {errors}')
            chrome.close()
            raise print(f"[bold red]|ERROR| OnOnlyOffice Desktop opens with errors in the js console")
        chrome.close()

    @retry(max_attempts=50, interval=2, stdout=False)
    def _connection_debug_mode(self, chrome):
        chrome.open('http://127.0.0.1:8080')
        chrome.click_by_xpath(XPath.hello_document)
        time.sleep(2)

    def _check_console_log(self, chrome) -> list:
        js_logs = chrome.get_js_log()
        chrome.driver.execute_script("console.clear();")
        errors = []
        for log in js_logs:
            if log['message'] in self.exceptions:
                print(f"[green]|CONSOLE LOG| {log['message']}")
            else:
                errors.append(log['message'])
                print(f"[bold red]{'-'*90}\n|CONSOLE LOG||ERROR| {log['message']}\n{'-'*90}")
        return errors

    def check_installed(self):
        installed_version = self.package.get_version()
        if self.version != installed_version:
            Image.make_screenshot(f"{join(self.report.dir, f'{self.version}_{self.host_name}_desktop_screen.png')}")
            self._write_results('NOT_INSTALLED')
            raise print(
                f"[bold red]|ERROR| OnlyOffice Desktop not installed. "
                f"Current version: {installed_version}"
            )

    def _write_results(self, results):
        self.report.write(self.package.name, self.version, HostInfo().name(pretty=True), results)
        pkg_name = re.sub(r"[\s/_]", "", self.package.name)
        Telegram().send_media_group(
            document_paths=self._get_report_files(),
            caption=f'Package: `{pkg_name}`\n'
                    f'Version: `{self.version}`\n'
                    f'Os: `{HostInfo().name(pretty=True)}`\n'
                    f'Result: `{results if results == "Passed" else "Error"}`'
        )

    def _get_report_files(self):
        return sorted(FileUtils.get_paths(self.report.dir), key=lambda x: x.endswith('.csv'))

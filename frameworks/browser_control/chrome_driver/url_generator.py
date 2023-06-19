# -*- coding: utf-8 -*-

class UrlGenerator:
    names = [
        'chromedriver_linux64.zip',
        'chromedriver_mac64.zip',
        'chromedriver_mac_arm64.zip',
        'chromedriver_win32.zip'
    ]

    def __init__(self):
        self.host = 'https://chromedriver.storage.googleapis.com'
        self.version = None
        self.package_name = None
        # 114.0.5735.90

    @property
    def url(self) -> str:
        return f"{self.host}/{self.version}/{self.package_name}"

    def _package_name(self):
        names = [
            'chromedriver_linux64.zip',
            'chromedriver_mac64.zip',
            'chromedriver_mac_arm64.zip',
            'chromedriver_win32.zip'
        ]
# -*- coding: utf-8 -*-
from os.path import isfile, join, dirname, realpath
from frameworks.host_control import HostInfo
from rich import print
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options



class Chrome:
    def __init__(self, chrome_options: Options = None):
        self.options = chrome_options
        self.driver = self._load_driver(path=join(dirname(realpath(__file__)), 'assets', 'web_driver', HostInfo().os, 'chromedriver'))

    def _load_driver(self, path) -> WebDriver:
        if isfile(path):
            return webdriver.Chrome(executable_path=path, options=self.options)
        raise print(f"|ERROR| WebDriver not exists: {path}")

    def open(self, url: str) -> None:
        self.driver.get(url)

    def choose_dropdown_item(self, dropdown: WebElement, dropdown_item: WebElement) -> None:
        ActionChains(self.driver).click(dropdown).perform()
        ActionChains(self.driver).click(dropdown_item).perform()

    def click_by_xpath(self, xpath: str, wait_element: int = 10, clicks: int = 1) -> None:
        button = WebDriverWait(self.driver, wait_element).until(EC.presence_of_element_located((By.XPATH, xpath)))
        for i in range(clicks):
            button.click()

    def make_screenshot(self, path: str) -> None:
        self.driver.save_screenshot(path)

    def get_element(
            self,
            xpath: str = None,
            id: str = None,
            link_text: str = None,
            name: str = None,
            tag_name: str = None,
            class_name: str = None,
            css_selector: str = None,
            wait_element: int = 10
    ) -> WebElement:
        locator = None

        if xpath:
            locator = (By.XPATH, xpath)
        elif id:
            locator = (By.ID, id)
        elif link_text:
            locator = (By.LINK_TEXT, link_text)
        elif name:
            locator = (By.NAME, name)
        elif tag_name:
            locator = (By.TAG_NAME, tag_name)
        elif class_name:
            locator = (By.CLASS_NAME, class_name)
        elif css_selector:
            locator = (By.CSS_SELECTOR, css_selector)

        if locator is None:
            raise ValueError("[red]|ERROR| No valid locator provided. Can't get the element")
        return WebDriverWait(self.driver, wait_element).until(EC.presence_of_element_located(locator))

    @staticmethod
    def enter_text(text: str, text_field: WebElement) -> None:
        text_field.send_keys(text)

    def get_js_log(self) -> "list | dict":
        return self.driver.get_log('browser')

    def close(self) -> None:
        self.driver.quit()

    def minimize_window(self) -> None:
        self.driver.minimize_window()

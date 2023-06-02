# -*- coding: utf-8 -*-
import time
from frameworks.StaticData import StaticData
from frameworks.host_control import FileUtils, HostInfo
from frameworks.editors.onlyoffice.desktop.package.url_generator import UrlGenerator
import config
from multiprocessing import Process
from os.path import join
from subprocess import call, Popen
import subprocess as sb
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class Installer:

    def __init__(self, sudo_password: str = None):
      self.tmp_dir = StaticData.tmp_dir
      self.pwd = sudo_password
      self.pkg_name = UrlGenerator(config.version).package_name

    def run(self):
        # call(f'{f"echo {self.pwd} | sudo -S " if self.pwd else ""}dpkg -i {join(self.tmp_dir, self.pkg_name)}', shell=True)
        process = Process(target=self.open_desktop)
        process.start()
        self.check_console()
        process.terminate()

    def check_console(self):
      print(1)
      driver_path = '/home/l02/scripts/opencv_documents_comparer/tmp/chromedriver'
      chrome_options = Options()
      chrome_options.add_argument("--auto-open-devtools-for-tabs")
      driver = webdriver.Chrome(executable_path=driver_path)
      driver.get('http://127.0.0.1:8080')
      button = driver.find_element(By.LINK_TEXT, 'Hello Documents')
      wait = WebDriverWait(driver, 10)  # Ожидание до 10 секунд
      new_element = wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Hello Documents')))
      print('click')
      button.click()
      time.sleep(20)
      logs = driver.get_log('browser')

      for log in logs:
        print(log['message'])
      driver.quit()

    def open_desktop(self):
      call('onlyoffice-desktopeditors --ascdesktop-support-debug-info', shell=True)

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import geckodriver_autoinstaller
import time
import os
import asyncio


class insta_vid:
    '''Uses igram.io to download videos from instagram and returns an error if something goes wrong.'''
    def __init__(self):
        self.start = time.time()
    
    def insta_getvid(self, URL):
        __session = requests.Session()
        __URL = "https://snapinsta.app/"
        path = "/src/bot/down/"
        __options = Options()
        __options.set_preference("browser.download.folderList", 2)
        __options.set_preference("browser.download.manager.showWhenStarting", False)
        __options.set_preference("browser.download.dir", path)
        __options.set_preference("browser.helperApps.neverAsk.saveToDisk", "video/mp4")
        __options.add_argument('-headless')
        geckodriver_autoinstaller.install()
        __driver = webdriver.Firefox(options=__options)
        __driver.get(__URL)
        __driver.find_element(By.ID, "url").send_keys(URL)
        __driver.find_element(By.ID, "url").send_keys(Keys.RETURN)
        __error = None
        try:
            #wait until the page has the download button
            #WebDriverWait(__driver, 80).until(EC.element_to_be_clickable((By.XPATH, "//*[starts-with(@class, 'abutton is-success')]")))
            __element_present = EC.presence_of_element_located((By.XPATH, "//*[starts-with(@class, 'abutton is-success')]"))
            WebDriverWait(__driver, 80).until(__element_present)
        except TimeoutException:
            __driver.close()
            raise InstaDownloadFailedError("Song not found or input error")
        __button = __driver.find_element(By.XPATH, "//*[starts-with(@class, 'abutton is-success')]")
        __URL = __button.get_attribute("href")
        print(__URL)
        __driver.set_page_load_timeout(5)
        try:
            __driver.get(__URL)
        except TimeoutException:
            pass
        files = os.listdir(path)
        print(files)
        start = time.time()
        diff = 0
        while any(".part" in f for f in files) and diff < 240:
            time.sleep(.1)
            print(files)
            print(f"checking for file {diff}")
            diff = time.time() - start
            files = os.listdir(path)
        if diff >= 240:
            __driver.quit()
            raise InstaDownloadFailedError("Timeout Reached")
        __driver.close()


class InstaDownloadFailedError(Exception):
    """Error thrown when song is not found"""
    pass

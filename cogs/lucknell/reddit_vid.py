import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import geckodriver_autoinstaller
import os
import time

class reddit_vid:
    '''Uses https://savemp4.red/ to download videos from reddit and returns an error if something goes wrong.'''

    def __init__(self, URL):
        __session = requests.Session()
        __URL = "https://savemp4.red/?url="
        path = "/src/bot/down/"
        __options = Options()
        __options.set_preference("browser.download.folderList", 2)
        __options.set_preference("browser.download.manager.showWhenStarting", False)
        __options.set_preference("browser.download.dir", path)
        __options.set_preference("browser.helperApps.neverAsk.saveToDisk", "video/mp4")
        __options.add_argument('-headless')
        geckodriver_autoinstaller.install()
        __driver = webdriver.Firefox(options=__options)
        if not "reddit.com" in URL:
            __driver.get(URL)
            URL = __driver.current_url
        __driver.get(__URL+URL)
        __error = None
        try:
            #wait until the page is fully loaded and the mini card is ready
            __element_present = EC.presence_of_element_located((By.XPATH, "//*[@class='btn btn-success btn-lg downloadButton']"))
            WebDriverWait(__driver, 60).until(__element_present)
        except TimeoutException:
            raise RedditDownloadFailedError("Song not found or input error")
        self.URL = __driver.find_elements(By.XPATH, "//*[@class='btn btn-success btn-lg downloadButton']")[0].get_attribute("href")
        __driver.set_page_load_timeout(5)
        try:
            __driver.get(self.URL)
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
        print(f"Timer was {diff}")
        if diff >= 240:
            __driver.quit()
            raise RedditDownloadFailedError("Timeout Reached")
        __driver.close()


class RedditDownloadFailedError(Exception):
    """Error thrown when song is not found"""
    pass

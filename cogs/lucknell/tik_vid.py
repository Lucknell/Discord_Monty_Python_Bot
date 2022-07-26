import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import geckodriver_autoinstaller


class tik_vid:
    '''Uses https://snaptik.app/ to download videos from tweets and returns an error if something goes wrong.'''

    def __init__(self, URL):
        __session = requests.Session()
        __URL = "https://snaptik.app/"
        __request = __session.get(__URL)
        __options = Options()
        __options.add_argument('-headless')
        geckodriver_autoinstaller.install()
        __driver = webdriver.Firefox(options=__options)
        __driver.get(__URL)
        __driver.find_element_by_id("url").send_keys(URL)
        __driver.find_element_by_id("submiturl").click()
        __error = None
        try:
            #wait until the page is fully loaded and the mini card is ready
            __element_present = EC.presence_of_element_located((By.XPATH, "//*[starts-with(@class, 'snaptik-right')]/div/a"))
            WebDriverWait(__driver, 20).until(__element_present)
        except TimeoutException:
            __driver.close()
            raise TikTokDownloadFailedError("Song not found or input error")
        __button = __driver.find_element(By.XPATH, "//*[starts-with(@class, 'snaptik-right')]/div/a")
        #__button = __driver.find_element_by_class_name("abutton is-success is-fullwidth")
        self.URL = __button.get_attribute("href")
        __driver.close()


class TikTokDownloadFailedError(Exception):
    """Error thrown when song is not found"""
    pass

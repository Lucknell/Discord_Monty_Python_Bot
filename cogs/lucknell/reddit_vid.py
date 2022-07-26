import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import geckodriver_autoinstaller


class reddit_vid:
    '''Uses https://savemp4.red/ to download videos from reddit and returns an error if something goes wrong.'''

    def __init__(self, URL):
        __session = requests.Session()
        __URL = "https://savemp4.red/?url="
        __options = Options()
        __options.add_argument('-headless')
        geckodriver_autoinstaller.install()
        __driver = webdriver.Firefox(options=__options)
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
        self.URL = __driver.find_elements_by_xpath("//*[@class='btn btn-success btn-lg downloadButton']")[0].get_attribute("href")
        __driver.close()


class RedditDownloadFailedError(Exception):
    """Error thrown when song is not found"""
    pass

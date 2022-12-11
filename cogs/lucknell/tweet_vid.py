import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import geckodriver_autoinstaller


class tweet_vid:
    '''Uses https://twittervideodownloader.com/ to download videos from tweets and returns an error if something goes wrong.'''

    def __init__(self, URL):
        __session = requests.Session()
        __URL = "https://twittervideodownloader.com/"
        __request = __session.get(__URL)
        __options = Options()
        __options.add_argument('-headless')
        geckodriver_autoinstaller.install()
        __driver = webdriver.Firefox(options=__options)
        __driver.get(__URL)
        __driver.find_element(By.CLASS_NAME, "input-group-field").send_keys(URL)
        __driver.find_element(By.CLASS_NAME, "button").click()
        __error = None
        try:
            #wait until the page is fully loaded and the mini card is ready
            __element_present = EC.presence_of_element_located((By.CLASS_NAME, "row"))
            WebDriverWait(__driver, 5).until(__element_present)
        except TimeoutException:
            raise TweetDownloadFailedError("Song not found or input error")
        __buttons = __driver.find_elements(By.XPATH, "//*[starts-with(@class, 'row')]/div/a")
        quality = 1
        if len(__buttons) == 1:
            if "facebook" in __buttons[0].text.lower():
                raise TweetDownloadFailedError("Download Failed.")
            self.URL = __buttons[0].get_attribute("href")
            __driver.close()
            return
        for button in __buttons:
            if "facebook" in button.text.lower():
                raise TweetDownloadFailedError("Download Failed.")
            __string = button.get_attribute("href").split("/vid/")[1].split("x")[0]
            if int(__string) > quality:
                quality = int(__string)
                self.URL = button.get_attribute("href")
        __driver.close()


class TweetDownloadFailedError(Exception):
    """Error thrown when song is not found"""
    pass

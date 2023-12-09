from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import geckodriver_autoinstaller
import time
import wget


class tweet_vid2:
    '''Uses https://tweetpik.com/twitter-downloader to download videos from tweets and returns an error if something goes wrong.'''

    def __init__(self, URL):
        path = "/src/bot/down/"
        self.has_photo = True
        __options = Options()
        __options.add_argument('-headless')
        __options.set_preference("browser.download.folderList", 2)
        __options.set_preference("browser.download.manager.showWhenStarting", False)
        __options.set_preference("browser.download.dir", path)
        __options.set_preference("browser.helperApps.neverAsk.saveToDisk", "video/mp4")
        geckodriver_autoinstaller.install()
        __driver = webdriver.Firefox(options=__options)
        __driver.get(URL)
        time.sleep(5)
        #try:
            #wait until the page is fully loaded and the mini card is ready
        #    __element_present = EC.presence_of_element_located((By.XPATH, "//a[starts-with(@href, '/settings')]"))
        #    WebDriverWait(__driver, 5).until(__element_present)
        #except TimeoutException:
        #    raise TweetDownloadFailedError("Song not found or input error")
        tweets = __driver.find_elements(By.XPATH, "//article")
        try:
            photos = tweets[0].find_elements(By.XPATH, "//img[starts-with(@src, 'https://pbs.twimg.com/media/')]")
        except IndexError:
            photos = []
        if len(photos) == 0:
            raise Tweet2DownloadFailedError("No content found")
        self.has_photo = True
        for photo in photos:
            string = photo.get_attribute("src").split("?format")[0] + ".jpg"
            wget.download(string, path)
        __driver.close()



class Tweet2DownloadFailedError(Exception):
    """Error thrown when song is not found"""
    pass

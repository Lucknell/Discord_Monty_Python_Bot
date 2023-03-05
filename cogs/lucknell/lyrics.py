import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import geckodriver_autoinstaller
import re 


class lyric_finder:
    '''Uses azlyrics.com to find lyrics for a song and returns an error if not found'''

    def __init__(self, search, provider="azlyrics"):
        if provider.lower() == "azlyrics":
            self.search_azlyrics(search)
        elif provider.lower() == "genius":
            self.search_genius(search)
        else:
            pass

    def search_azlyrics(self, search):
        __azlyricsString = "<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->"
        __session = requests.Session()
        __URL = "https://search.azlyrics.com/search.php?q="
        __Final_URL = __URL + search.replace(" ", "+")
        __request = __session.get(__Final_URL)
        __soup = BeautifulSoup(__request.content, 'html.parser')
        try:
            __links = __soup.find(class_="table table-condensed").find_all('a')
        except AttributeError:
            raise SongNotFoundError("Song not found or input error")
        self.URL = __links[0]['href']
        __request = __session.get(self.URL)
        __soup = BeautifulSoup(__request.content, 'html.parser')
        __page = __soup.find(
            class_="col-xs-12 col-lg-8 text-center")
        self.title = __page.findAll("b")[1].text
        self.lyrics = __page.find_all("div")[5].text

    def search_genius(self, search):
        options = Options()
        options.add_argument('-headless')
        geckodriver_autoinstaller.install()
        __driver = webdriver.Firefox(options=options)
        __URL = "https://genius.com/search?q="
        __Final_URL = __URL + search.strip().replace(" ", "%20")
        __driver.get(__Final_URL)
        try:
            #wait until the page is fully loaded and the mini card is ready
            __element_present = EC.presence_of_element_located((By.CLASS_NAME, "mini_card"))
            WebDriverWait(__driver, 5).until(__element_present)   
        except TimeoutException:
            raise SongNotFoundError("Song not found or input error")

        __mini_cards = __driver.find_elements(By.CLASS_NAME, "mini_card")
        try:
            self.URL = __mini_cards[1].get_attribute("href")
        except IndexError:
            __driver.quit()
            raise SongNotFoundError("Song not found or input error")
        __driver.get(self.URL)
        try:
            #wait until the page is fully loaded and the mini card is ready
            __element_present = EC.presence_of_element_located((By.XPATH, "//span[starts-with(@class, 'SongHeaderdesktop')]"))
            WebDriverWait(__driver, 5).until(__element_present)   
        except TimeoutException:
            raise SongNotFoundError("Song not found or input error")
        self.title = __driver.find_element(By.XPATH, "//span[starts-with(@class, 'SongHeaderdesktop')]").text
        self.lyrics = __driver.find_element(By.XPATH, "//div[starts-with(@class, 'Lyrics__Container')]").text
        self.author = __driver.find_element(By.XPATH, "//a[starts-with(@href, 'https://genius.com/artists/')]").text

class SongNotFoundError(Exception):
    """Error thrown when song is not found"""
    pass

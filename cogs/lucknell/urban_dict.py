import requests
from bs4 import BeautifulSoup
import re

class urban_finder:
    '''Uses azlyrics.com to find lyrics for a song and returns an error if not found'''

    def __init__(self, search):
        self.search_urban(search)

    def search_urban(self, search):
        __URL = "https://www.urbandictionary.com/define.php?term="
        __Final_URL = __URL + search.strip().replace(" ", "%20")
        __session = requests.Session()
        __request = __session.get(__Final_URL)
        __soup = BeautifulSoup(__request.content, 'html.parser')
        __page = __soup.find(class_=re.compile("word text-denim"))
        self.title = __page.text
        __page = __soup.find(class_=re.compile("break-words meaning mb-4"))
        self.definition = __page.text
        __page = __soup.find(class_=re.compile("break-words example italic mb-4"))
        self.example = __page.text
        


class SongNotFoundError(Exception):
    """Error thrown when song is not found"""
    pass

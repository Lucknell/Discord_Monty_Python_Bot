import requests
from bs4 import BeautifulSoup
import re

class word_search:
    '''Uses azlyrics.com to find lyrics for a song and returns an error if not found'''

    def __init__(self, search):
        self.define(search)

    def define(self, search):
        __URL = "https://www.merriam-webster.com/dictionary/"
        __Final_URL = __URL + search.strip()
        __session = requests.Session()
        __request = __session.get(__Final_URL)
        __soup = BeautifulSoup(__request.content, 'html.parser')
        __page = __soup.find("h1",class_=re.compile("hword"))
        self.title = __page.text
        __page = __soup.find("a",class_=re.compile("important-blue-link"))
        self.type = __page.text
        __page = __soup.find(id=re.compile("dictionary-entry-1"))
        self.definition = __page.text



class SongNotFoundError(Exception):
    """Error thrown when song is not found"""
    pass

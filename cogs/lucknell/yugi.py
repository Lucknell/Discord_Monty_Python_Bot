import re
import requests
from bs4 import BeautifulSoup
import utils


class yugioh_finder:

    def __init__(self, search):
        __session = requests.Session()
        __base_URL = "https://yugioh.fandom.com/wiki/Special:Search?query={}&scope=internal&navigationSearch=true"
        __final_URL = __base_URL.format(search.strip().replace(" ", "+"))
        __request = __session.get(__final_URL)
        soup = BeautifulSoup(__request.content, 'html.parser')
        __yugidata = soup.findAll(class_="unified-search__result__title")
        if not __yugidata:
            raise ShadowRealmError
        self.URL = __yugidata[0]['href']
        __request = __session.get(self.URL)
        soup = BeautifulSoup(__request.content, 'html.parser')
        __yugidata = soup.find(id="firstHeading")
        self.heading = __yugidata.text.strip()
        __yugidata = soup.findAll("img")
        if __yugidata:
            try:
                #If image is a blue i icon, don't use it
                if __yugidata[2]["src"] == "https://static.wikia.nocookie.net/yugioh/images/c/c8/Ambox_notice.png/revision/latest/scale-to-width-down/40?cb=20100710011553":
                    self.picture = __yugidata[3]["src"]
                else:
                    self.picture = __yugidata[2]["src"]
            except KeyError:
                self.picture = None
            except IndexError:
                self.picture = None
        else:
            self.picture = None
        __yugidata = soup.findAll(title="ATK")
        __yugiboy  = soup.findAll(string="Relatives")
        self.isACard = False
        self.type = "Not a card"
        self.level = "Not a card"
        self.stats = "Not a card"
        self.card_type = "Not a card"
        self.description = "You shouldn't be seeing this"
        if __yugidata and not __yugiboy: # We have a card lets fill some data
            self.isACard = True
            self.description = soup.findAll(class_="navbox-list")[0].text
            __card_table = soup.findAll(class_="cardtablerowdata")
            __card_header = soup.findAll(class_="cardtablerowheader")
            for current, next in zip(__card_header, __card_table):
                try:
                    if current.text.strip() == "Level" or current.text.strip() == "Rank":
                        self.level = next.text.strip()
                    if current.text.strip() == "Types" or current.text.strip() == "Type":
                        self.type = next.text.strip()
                    if current.text.strip() == "ATK / DEF":
                        self.stats = next.text.strip()
                    if current.text.strip() == "Card type":
                        self.card_type = next.text.strip()
                except UnicodeEncodeError:
                    continue
            #self.level = __card_table[16].text
            #self.stats = __card_table[17].text
            #self.type = __type[0]
        else:
            self.description = soup.find(string=self.heading)



class ShadowRealmError(Exception):
    """Error thrown when search may have been banished to the shadow realm"""
    pass

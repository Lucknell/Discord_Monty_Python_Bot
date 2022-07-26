import requests
from bs4 import BeautifulSoup


class pokemon_finder:

    def __init__(self, search):
        __session = requests.Session()
        __base_URL = "https://pokemon.fandom.com/wiki/Special:Search?query={}&scope=internal&navigationSearch=true"
        __final_URL = __base_URL.format(search.strip().replace(" ", "+"))
        __request = __session.get(__final_URL)
        soup = BeautifulSoup(__request.content, 'html.parser')
        __pokedata = soup.findAll(class_="unified-search__result__title")
        if not __pokedata:
            raise PokemonNotFoundError
        self.URL = __pokedata[0]['href']
        __request = __session.get(self.URL)
        soup = BeautifulSoup(__request.content, 'html.parser')
        __pokedata = soup.find(id="firstHeading")
        self.heading = __pokedata.text
        __pokedata = soup.find(class_="pi-image-thumbnail")
        if __pokedata:
            self.picture = __pokedata["src"]
        else:
            self.picture = None
        __pokedata = soup.findAll(class_="pi-data-value pi-font")
        self.type = None
        if __pokedata:
            if __pokedata[0].a:
                types = __pokedata[0].findAll("a")
                if len(types) > 1:
                    self.type = __pokedata[0].a["href"].replace("/wiki/", "").replace(
                        "_type", "") + "/" + types[1]["href"].replace("/wiki/", "").replace("_type", "")
                else:
                    self.type = __pokedata[0].a["href"].replace(
                        "/wiki/", "").replace("_type", "")
            else:
                self.type = __pokedata[0].text
        __pokedata = soup.find(class_="pokedex-entry")
        if __pokedata:
            self.pokedex = {}
            __pokedata = __pokedata.findAll("li")
            for entry in __pokedata:
                self.pokedex[entry.span.text] = entry.p.text
        else:
            self.pokedex = None


class PokemonNotFoundError(Exception):
    """Error thrown when pokemon is not found"""
    pass

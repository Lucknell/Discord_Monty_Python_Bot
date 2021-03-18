import requests
from bs4 import BeautifulSoup


class pokemon_finder:

    def __init__(self, search):
        s = requests.Session()
        __base_URL = "https://pokemon.fandom.com/wiki/Special:Search?query={}&scope=internal&navigationSearch=true"
        __final_URL = __base_URL.format(search.strip().replace(" ", "+"))
        r = s.get(__final_URL)
        soup = BeautifulSoup(r.content, 'html.parser')
        p = soup.findAll(class_="unified-search__result__title")
        if not p:
            raise PokemonNotFoundError
        self.URL = p[0]['href']
        r = s.get(self.URL)
        soup = BeautifulSoup(r.content, 'html.parser')
        p = soup.find(id="firstHeading")
        self.heading = p.text
        p = soup.find(class_="pi-image-thumbnail")
        if p:
            self.picture = p["src"]
        else:
            self.picture = None
        p = soup.findAll(class_="pi-data-value pi-font")
        self.type = None
        if p:
            if p[0].a:
                types = p[0].findAll("a")
                if len(types) > 1:
                    self.type = p[0].a["href"].replace("/wiki/", "").replace(
                        "_type", "") + "/" + types[1]["href"].replace("/wiki/", "").replace("_type", "")
                else:
                    self.type = p[0].a["href"].replace(
                        "/wiki/", "").replace("_type", "")
            else:
                self.type = p[0].text
        p = soup.find(class_="pokedex-entry")
        if p:
            self.pokedex = {}
            p = p.findAll("li")
            for entry in p:
                self.pokedex[entry.span.text] = entry.p.text
        else:
            self.pokedex = None


class PokemonNotFoundError(Exception):
    """Error thrown when pokemon is not found"""
    pass

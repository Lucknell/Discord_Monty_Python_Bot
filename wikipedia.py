import requests
from bs4 import BeautifulSoup


class wikipedia:
    '''Scrapes some data from Wikipeida using BeautifulSoup4.'''
    def __init__(self, search):
        __session = requests.Session()
        __URL = "https://en.wikipedia.org/w/api.php"
        __PARAMS = {
            "action": "opensearch",
            "namespace": "0",
            "search": search,
            "limit": "1",
            "format": "json"
        }
        __request = __session.get(url=__URL, params=__PARAMS)
        self.json = __request.json()
        try:
            self.url = self.json[3][0]
        except IndexError:
            self.json = None
            return
        self.page = requests.get(self.url)
        __soup = BeautifulSoup(self.page.content, 'html.parser')
        __text = __soup.find(id="mw-content-text").find_all('p')
        self.text = ""
        self.summary = ""
        for i in range(0, len(__text), 1):
            if not __text[i].span:
                if len(self.summary) < 1000:
                    self.summary += __text[i].text
                self.text += __text[i].text
                # break

        try:
            __infobox = __soup.find(
                'table', {'class': 'infobox'}).find_all("tr")
        except AttributeError:
            __infobox = None
        if __infobox:
            self.infobox = []
            for info in __infobox:
                self.infobox.append(self.__remove_tags(info))
        else:
            self.infobox = None
        self.orig_tables = __soup.find_all("table")
        self.tables = []
        for table in self.orig_tables:
            __columns = ""
            __rows = ""
            __caption = ""
            __tags = str(table).split("\n")
            for tag in __tags:
                if "scope=\"col\"" in tag:
                    __string = self.__remove_tags(tag)
                    __columns += __string.replace("v      t      e      ", "")
                    __columns += "\t"
                elif "</tr>" in tag:
                    try:
                        if not __rows[-1] == "\n":
                            __rows += "\n"
                    except IndexError:
                        continue
                elif "<caption>" in tag:
                    __caption += self.__remove_tags(tag)
                else:
                    __string = self.__remove_tags(tag)
                    if len(__string) == 0:
                        continue
                    __rows += __string
                    __rows += "\t"
            self.tables.append(wiki_tables(__rows, __columns, __caption))


    def __remove_tags(self, tag_str):
        '''removes html tags and add a space after removal'''
        __string = ""
        __skip = False
        for letter in str(tag_str):
            try:
                if letter == "<":
                    __skip = True
                elif __skip and letter == ">":
                    __skip = False
                    __string += " "
                elif not __skip:
                    __string += letter
            except TypeError:
                continue
        return __string.strip()


class wiki_tables:
    def __init__(self, rows, columns, caption):
        self.rows = rows
        self.columns = columns
        self.caption = caption

    def __repr__(self):
        return "Caption:\n{}\nColumns:\n{}\nRows:\n{}\n".format(self.caption, self.columns, self.rows)

    def __str__(self):
        return "{}\n{}\n{}\n".format(self.caption, self.columns, self.rows)

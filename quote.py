import requests
from bs4 import BeautifulSoup


class quote_finder:


    def __init__(self, category, search=None):
        s = requests.Session()
        __base_URL = "https://www.quotes.net/serp.php?st={}&qtype={}"
        __quote_URL = "https://www.quotes.net"
        if category.lower() == "random":
            if not search:
                __type = "1"
            elif search.lower() == "movie":
                __type = "2"
            elif search.lower() == "tv":
                __type = "4"
            else:
                __type = "1"
            r = s.get("https://www.quotes.net/random.php?type={}".format(__type))
            if __type == "1":
                soup = BeautifulSoup(r.content, 'html.parser')
                p = soup.find(id="disp-quote-body")  
            else:
                soup = BeautifulSoup(r.content, 'html.parser')
                p = soup.find(class_="disp-mquote-int")
            self.quote = p.text
            self.quote_URL = "URL unavailable"
        elif category.lower() == "movie":
            __final_URL = __base_URL.format(
                search.strip().replace(" ", "+"), "2")
            r = s.get(__final_URL)
            soup = BeautifulSoup(r.content, 'html.parser')
            p = soup.find(class_="movie-quote")
            if not p:
                raise QuoteNotFoundError
            self.quote_URL = __quote_URL + p.a['href']
            __tags = p.a.find_all("p")
            self.quote = ""
            for tag in __tags:
                if tag.text == "":
                    continue
                self.quote += (tag.text + "\n")
        elif category.lower() == "tv":
            __final_URL = __base_URL.format(
                search.strip().replace(" ", "+"), "4")
            r = s.get(__final_URL)
            soup = BeautifulSoup(r.content, 'html.parser')
            p = soup.find(class_="movie-quote")
            if not p:
                raise QuoteNotFoundError
            self.quote_URL = __quote_URL + p.a['href']
            __tags = p.a.find_all("p")
            self.quote = ""
            for tag in __tags:
                if tag.text == "":
                    continue
                self.quote += (tag.text + "\n")
        elif category.lower() == "book":
            __base_URL = "https://www.quotes.net/quotations/{}"
            __final_URL = __base_URL.format(search.strip())
            r = s.get(__final_URL)
            soup = BeautifulSoup(r.content, 'html.parser')
            p = soup.find(class_="author-quote")
            if not p:
                raise QuoteNotFoundError
            self.quote_URL = __quote_URL + p.a['href']
            self.quote = p.a.text

        else:
            raise InvalidCategoryGiven


class QuoteNotFoundError(Exception):
    """Error thrown when quote is not found"""
    pass

class InvalidCategoryGiven(Exception):
    """Error thrown when the category is not valid"""
    pass

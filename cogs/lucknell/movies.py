import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class Movie_Finder:

    def __init__(self):
        """Scrapes cinemark.com for movies that are now playing or coming soon"""
        self.response = requests.get("https://www.cinemark.com/movies/")
        self.soup = BeautifulSoup(self.response.content, 'html.parser')
        self.movie_block = self.soup.find(class_ ='col-sm-8 contentMain moviesBlockLayout').findAll(class_ = lambda L: L and 'movieBlock' in L) 
        self.movies = dict()
        for movie in self.movie_block:
            try:
                self.JSON = json.loads(movie.find(class_ = lambda L: L and 'play-trailer' in L)['data-json-model'])
                self.movies[movie['data-movie-title']] = Movie(
                    movie['data-movie-title'],
                    movie['data-movie-releasedate'],
                    self.JSON.get("posterMediumImageUrl"),
                    self.JSON.get("trailerUrl"),
                    self.JSON.get("movieRating"),
                    self.JSON.get("movieRunTime")) 
            except TypeError:
                pass
        self.movies = dict(sorted(self.movies.items(), key = lambda L: datetime.strptime((L[1].release_date).split()[0], "%m/%d/%Y")))


class Movie:

    def __init__(self, title, release_date, poster, trailer, rating, runtime):
        self.title = title
        self.release_date = release_date
        self.poster = poster
        self.trailer = trailer
        self.rating = rating
        self.runtime = runtime


class MovieNotFoundError(Exception):
    """Error thrown when a movie is not found"""
    pass
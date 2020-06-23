import urllib.parse

import requests
from bs4 import BeautifulSoup


def get_url_contents(url):
    res = requests.get(url)
    return res.text


def get_titles(url):
    url_contents = get_url_contents(url)

    songs = get_songs(url_contents)
    artist = get_artist(url_contents)

    titles = []
    for song in songs:
        title = extract_title(song)
        titles.append(f"{artist} - {title}")

    return titles


def get_songs(url_contents):
    soup = BeautifulSoup(url_contents, "html.parser")
    setlist_list = soup.find("div", "setlistList")
    songs = setlist_list.find_all("li", "setlistParts song")
    return songs


def get_artist(url_contents):
    soup = BeautifulSoup(url_contents, "html.parser")
    artist = soup.title.string.split(" ")[0]
    return artist


def extract_title(song):
    url = song.div.a["href"]
    query_string = urllib.parse.urlparse(url).query
    title = urllib.parse.parse_qs(query_string)["song"][0]
    return title

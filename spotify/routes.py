import base64
import json
import random
import string
import uuid
from urllib.parse import urlencode

import requests
from flask import Blueprint
from flask import redirect
from flask import request
from flask.helpers import get_debug_flag

from spotify.logger import logger
from spotify.scraper import get_titles
from spotify.settings import DevConfig
from spotify.settings import ProdConfig

blueprint = Blueprint("routes", __name__)
CONFIG = DevConfig if get_debug_flag() else ProdConfig
STATE_KEY = "spotify_auth_state"


@blueprint.route("/")
def index():
    return "This is a root placeholder"


@blueprint.route("/login")
def login():
    state = random_string(16)
    provider_url = "https://accounts.spotify.com/authorize"
    scopes = [
        "playlist-modify-private",
        "playlist-read-private",
        "user-read-private",
        "user-read-email",
    ]
    params = urlencode(
        {
            "response_type": "code",
            "client_id": CONFIG.CLIENT_ID,
            "scope": " ".join(scopes),
            "redirect_uri": f"http://{CONFIG.SERVER_HOST}:{CONFIG.PORT}/callback",
            "state": state,
        }
    )
    url = f"{provider_url}?{params}"

    res = redirect(url)
    res.set_cookie(STATE_KEY, state)

    return res


@blueprint.route("/callback")
def callback():
    code = request.args.get("code")
    state = request.args.get("state")
    stored_state = request.cookies.get(STATE_KEY) if request.cookies else None

    if not stored_state or state != stored_state:
        return f"State mismatch: expected '{stored_state}' but received '{state}'"

    try:
        logger.debug(f"code: {code}")
        token_data = request_access_token(code)
    except requests.exceptions.HTTPError as err:
        logger.error(f"There was an error requesting the access token: {err}")
        return "There was an error requesting the access token"

    logger.debug(f"response: {token_data}")

    try:
        user_profile = request_user_profile(token_data)
    except requests.exceptions.HTTPError as err:
        logger.error(f"There was an error requesting the user profile: {err}")
        return "There was an error requesting the user profile"

    logger.debug(f"user_profile: {user_profile}")
    access_token = token_data["access_token"]
    user_id = user_profile["id"]

    try:
        playlist_metadata = create_playlist(user_id, access_token)
    except requests.exceptions.HTTPError as err:
        logger.error(f"There was an error creating the playlist: {err}")
        return "There was an error creating the playlist"

    logger.debug(f"Playlist created at {playlist_metadata['href']}")

    user_country = user_profile["country"]

    # TODO: think of how you want to handle URL input
    url = "https://www.setlist.fm/setlist/chvrches/2019/wiltern-theatre-los-angeles-ca-39a495b.html"

    titles = get_titles(url)
    tracks = search_tracks(titles, user_country, access_token)

    logger.debug(f"Found tracks: {tracks}")

    playlist_id = playlist_metadata["id"]

    try:
        snapshot = add_tracks_to_playlist(playlist_id, access_token, tracks)
    except requests.exceptions.HTTPError as err:
        logger.error(f"There was an error adding tracks to the playlist: {err}")
        # TODO: delete created playlist when this happens
        return "There was an error adding tracks to the playlist"

    logger.debug(f"snapshot: {snapshot}")

    return "Playlist created"


def request_access_token(code):
    url = "https://accounts.spotify.com/api/token"
    authorization = str(
        base64.b64encode(f"{CONFIG.CLIENT_ID}:{CONFIG.CLIENT_SECRET}".encode("utf-8")),
        "utf-8",
    )
    payload = {
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": f"http://{CONFIG.SERVER_HOST}:{CONFIG.PORT}/callback",
    }
    headers = {"Authorization": f"Basic {authorization}"}

    response = requests.request("POST", url, data=payload, headers=headers)
    response.raise_for_status()
    token_data = response.json()

    return token_data


def request_user_profile(body):
    access_token = body["access_token"]
    url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    logger.debug(f"access_token: {access_token}")

    response = requests.request("GET", url, headers=headers)
    response.raise_for_status()
    user_profile = response.json()

    return user_profile


def create_playlist(
    user_id,
    access_token,
    name=str(uuid.uuid4()),
    description="Made with spotify-playground",
):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    payload = {"name": name, "public": False, "description": description}
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    response.raise_for_status()
    playlist_metadata = response.json()

    return playlist_metadata


def search_tracks(titles, country, access_token):
    tracks = []

    for title in titles:
        try:
            track = search_track(title, country, access_token)
            tracks.append(track)
        except requests.exceptions.HTTPError as err:
            logger.warn(f"there was an error searching for the track: {err}")

    return tracks


def search_track(query, country, access_token):
    def get_most_popular_track(tracks_dict):
        items = tracks_dict["tracks"]["items"]
        sorted_items = sorted(items, key=lambda x: x["popularity"], reverse=True)
        most_popular_track = sorted_items[0]
        return most_popular_track

    url = "https://api.spotify.com/v1/search"
    params = urlencode({"q": query, "type": "track", "market": country})
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{url}?{params}"

    response = requests.request("GET", url, headers=headers)
    response.raise_for_status()

    tracks = response.json()
    track = get_most_popular_track(tracks)

    return track


def add_tracks_to_playlist(playlist_id, access_token, tracks):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    uris = ",".join([track["uri"] for track in tracks])
    params = urlencode({"uris": uris})
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{url}?{params}"

    response = requests.request("POST", url, headers=headers)
    response.raise_for_status()

    snapshot = response.json()

    return snapshot


def random_string(length=10):
    return "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(length)
    )

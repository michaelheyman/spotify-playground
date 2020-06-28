import uuid

import requests
import spotipy
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import session

from spotify.logger import logger
from spotify.scraper import get_titles

blueprint = Blueprint("routes", __name__, template_folder="templates")

scopes = ["playlist-modify-private", "playlist-read-private"]
oauth_manager = spotipy.oauth2.SpotifyOAuth(scope=",".join(scopes))
spotify = spotipy.Spotify(oauth_manager=oauth_manager)


@blueprint.route("/")
def index():
    if request.args.get("code"):
        session["token_info"] = oauth_manager.get_access_token(request.args["code"])
        return redirect("/")

    if not session.get("token_info"):
        auth_url = oauth_manager.get_authorize_url()
        return render_template("index.html", auth_url=auth_url)

    display_name = spotify.me()["display_name"]
    return render_template("signed.html", display_name=display_name)


@blueprint.route("/playlists")
def playlists():
    if not session.get("token_info"):
        return redirect("/")
    else:
        return spotify.current_user_playlists()


@blueprint.route("/sign_out")
def sign_out():
    session.clear()
    return redirect("/")


@blueprint.route("/submit", methods=["POST"])
def submit():
    # setlist_url = request.form["setlist_url"]
    setlist_url = (
        "https://www.setlist.fm/setlist/" + "chvrches/2019/" + ""
        "wiltern-theatre-los-angeles-ca-39a495b.html"
    )
    token_info = session["token_info"]
    print(f"token_info: {token_info}")
    print(f"form: {setlist_url}")

    titles = get_titles(setlist_url)
    tracks = search_tracks(titles)
    username = spotify.me()["id"]
    playlist = spotify.user_playlist_create(
        username,
        name=str(uuid.uuid4()),
        public=False,
        description="Made with spotify-playground",
    )
    playlist_id = playlist["id"]
    spotify.user_playlist_add_tracks(
        username, playlist_id, tracks=[track["uri"] for track in tracks]
    )

    return "YAY"


def search_tracks(titles):
    def get_most_popular_track(tracks_dict):
        items = tracks_dict["tracks"]["items"]
        sorted_items = sorted(items, key=lambda x: x["popularity"], reverse=True)
        most_popular_track = sorted_items[0]
        return most_popular_track

    tracks = []

    for title in titles:
        try:
            track = spotify.search(q=title, type="track")
            track = get_most_popular_track(track)
            tracks.append(track)
        except requests.exceptions.HTTPError as err:
            logger.warn(f"there was an error searching for the track: {err}")

    return tracks

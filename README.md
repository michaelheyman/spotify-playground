# spotify-playground

## Overview

This application is an experiment in using the Spotify API to automatically create playlists based on set lists found on [setlist.fm](https://www.setlist.fm/).

## How to Develop

### Create an Environment File

Create a `.env` file in the project root, and override the following variables as needed.

| Variable          | Type         | Description                                                                                                                        |
| ----------------- | ------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| CLIENT_ID         | **Required** | The application client ID, which can be found in the [Spotify dashboard](https://developer.spotify.com/dashboard/applications)     |
| CLIENT_SECRET     | **Required** | The application client secret, which can be found in the [Spotify dashboard](https://developer.spotify.com/dashboard/applications) |

The `.env` file will be automatically loaded.

These Spotify credentials are associated with a Spotify application. An application can be created [here](https://developer.spotify.com/dashboard/applications).

### Setup and Run

1. Install packages: `pip install -r requirements.txt`
1. Run application in debug mode: `env FLASK_DEBUG=1 flask run`
1. Access the http://localhost:5000/login endpoint and authorize the scopes
1. Get redirected to http://localhost:5000/callback

### Before Committing Changes

1. Ensure that `pre-commit` is installed: `pip install pre-commit`
1. Install `pre-commit`: `pre-commit install`

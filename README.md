# spotify-playground

## How to Develop

### Create an Environment File

Create a `.env` file in the project root, and override the following variables as needed.

| Variable          | Type         | Description                                                                                                                        |
| ----------------- | ------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| CLIENT_ID         | **Required** | The application client ID, which can be found in the [Spotify dashboard](https://developer.spotify.com/dashboard/applications)     |
| CLIENT_SECRET     | **Required** | The application client secret, which can be found in the [Spotify dashboard](https://developer.spotify.com/dashboard/applications) |

The `.env` file will be automatically loaded.

### Setup and Run

1. Install packages: `pip install -r requirements.txt`
1. Run application: `flask run`
1. Access the http://localhost:5000/login endpoint and authorize the scopes
1. Get redirected to http://localhost:5000/callback

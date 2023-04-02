from flask import Flask, request, redirect, session,make_response
import requests
import base64
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename
from getmetadata import getmetadata2
from getUserTopItems import get_user_top_items
from getSameArtistSong import getTopSong
import random
from flask_cors import CORS
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
app = Flask(__name__)

CORS(app)

# app.secret_key = SECRET_KEY
app.secret_key = 'ytjfhygfdggfedtt5uy56y5346jgbvcvew34ey'

# Replace these values with your own
# client_id = os.getenv('CLIENT_ID')
# client_secret = os.getenv('CLIENT_SECRET')
# redirect_uri = os.getenv('REDIRECT_URI')

client_id = 'd01d96529f0a4984b141c4063863100d'
client_secret = '8828063e4d6f4118a8cdd6469bac0196'
redirect_uri = 'http://localhost:8080/'

auth_url = "https://accounts.spotify.com/authorize"
token_url = "https://accounts.spotify.com/api/token"


@app.route("/")
def index():
    return "Hello World!"


@app.route("/authorize")
def authorize():
    # Step 1: Redirect user to Spotify's authorization page
    
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        # Add additional scopes here if needed
        "scope": "user-read-private user-read-email playlist-modify-private user-top-read"
    }
    url = requests.Request('GET', auth_url, params=params).prepare().url
    print(url)
    return redirect(url)


@app.route("/callback")
def callback():

    # Step 2: User has authorized the app, now get the access token
    code = request.args.get('code')
    headers = {
        'Authorization': 'Basic ' + base64.b64encode((client_id + ':' + client_secret).encode()).decode()
    }
    print("code ________",code)
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }
    response = requests.post(token_url, headers=headers, data=data)
    print('response__',response)
    response_data = response.json()
    access_token = response_data['access_token']
    refresh_token = response_data['refresh_token']
    # server side session management
    session['access_token'] = access_token

    return "Access token: {}".format(access_token)


@app.route('/top_songs')
def top_songs():
    genre = request.args.get('genre')
    # genre = "pop"
    auth_header = request.headers.get('Authorization')
    print("auth_header",auth_header)
    if auth_header:
        auth_token = auth_header
        
    else:
        print ("Authorization header not present")
    
    top_items = get_user_top_items(auth_token)
    headers = {
        'Authorization': 'Bearer ' + auth_token
    }
    params = (
        ('limit', '20'),
        ('seed_genres', genre),
        ('seed_tracks', top_items[0] + ',' + top_items[1] +
         ',' + top_items[2] + ',' + top_items[3]),
    )
    response = requests.get(
        'https://api.spotify.com/v1/recommendations', headers=headers, params=params)
    data = response.json()
    tracks = data['tracks']
    top_songs = [track['name'] for track in tracks]
    top_songs_id = [track['id'] for track in tracks]
    top_songs_album_images = [track['album']['images'] for track in tracks]
    track_images = []
    for images in top_songs_album_images:
        track_images.append(images[0]['url'])
    print(track_images)
    artists = [track['artists'] for track in tracks]
    artist_id = [artist[0]['id'] for artist in artists]
    random_artist = random.sample(artist_id, 5)
    artist_songs = []
    for id in random_artist:
        artist_songs.append(getTopSong(id, auth_token))
    return {'top_songs': {
        'name': top_songs,
        'id': top_songs_id,
        'images': track_images
    },
        'artist_songs': artist_songs}

@app.route('/top_playlists')
def top_playlists():
    genre = request.args.get('genre')
    # genre = "pop"
    url = "https://api.spotify.com/v1/browse/categories/"+genre+"/playlists"

    headers = {
    "Authorization": "Bearer " + session['access_token']
    }

    params = {
    "limit": 5,
    "offset": 0
    }

    response = requests.get(url.format(category_id="your_category_id"), headers=headers, params=params)

    print(response.json())
    return response.json()

@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    headers = {
        'Authorization': f'Bearer ' + session['access_token'],
    }

    response = requests.get('https://api.spotify.com/v1/me', headers=headers)
    user_id = response.json()['id']
    print(user_id)
    playlist_name = "test"
    song_ids = request.form.getlist('song_ids')
    headers = {
        'Authorization': 'Bearer ' + session['access_token'],
        'Content-Type': 'application/json',
    }
    data = {
        'name': playlist_name,
        'public': False,
    }
    response = requests.post(
        f'https://api.spotify.com/v1/users/{user_id}/playlists', headers=headers, json=data)
    playlist_id = response.json()['id']
    uris = [f'spotify:track:{song_id}' for song_id in song_ids]
    data = {
        'uris': uris,
    }
    response = requests.post(
        f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks', headers=headers, json=data)
    return {'playlist_id': playlist_id}


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    filename = secure_filename(file.filename)
    filePath = os.path.join(os.getcwd(), filename)
    file.save(filePath)
    newFilePath = os.path.join(os.getcwd(), 'song.wav')
    os.rename(filePath, newFilePath)
    genre = getmetadata2("song.wav")
    os.remove(newFilePath)
    return {
        'genre': genre
    }


if __name__ == "__main__":
    app.run(debug=True)

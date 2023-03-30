from flask import Flask, request, redirect , session
import requests
import base64
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename
from getmetadata import getmetadata2
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
app = Flask(__name__)
app.secret_key = SECRET_KEY


# Replace these values with your own
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
redirect_uri = os.getenv('REDIRECT_URI')

auth_url = "https://accounts.spotify.com/authorize" 
token_url = "https://accounts.spotify.com/api/token"

@app.route("/authorize")
def authorize():
    # Step 1: Redirect user to Spotify's authorization page
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        # Add additional scopes here if needed
        "scope": "user-read-private user-read-email playlist-modify-private"
    }
    url = requests.Request('GET', auth_url, params=params).prepare().url
    return redirect(url)

@app.route("/callback")
def callback():
    # Step 2: User has authorized the app, now get the access token
    code = request.args.get('code')
    headers = {
        'Authorization': 'Basic ' + base64.b64encode((client_id + ':' + client_secret).encode()).decode()
    }
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }
    response = requests.post(token_url, headers=headers, data=data)
    response_data = response.json()
    access_token = response_data['access_token']
    refresh_token = response_data['refresh_token']
    session['access_token'] = access_token

    return "Access token: {}".format(access_token)

@app.route('/top_songs')
def top_songs():
    genre = request.args.get('genre')
    headers = {
        'Authorization': 'Bearer ' + session['access_token']
    }
    params = (
        ('limit', '20'),
        ('seed_genres', genre),
    )
    response = requests.get('https://api.spotify.com/v1/recommendations', headers=headers, params=params)
    data = response.json()
    tracks = data['tracks']
    top_songs = [track['name'] for track in tracks]
    top_songs_id = [track['id'] for track in tracks]
    print(top_songs_id)
    return {'top_songs': top_songs}

@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    headers = {
        'Authorization': f'Bearer ' + session['access_token'],
    }

    response = requests.get('https://api.spotify.com/v1/me', headers=headers)
    user_id = response.json()['id']
    print(user_id)
    # playlist_name = request.form['playlist_name']
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
    response = requests.post(f'https://api.spotify.com/v1/users/{user_id}/playlists', headers=headers, json=data)
    playlist_id = response.json()['id']
    uris = [f'spotify:track:{song_id}' for song_id in song_ids]
    data = {
        'uris': uris,
    }
    response = requests.post(f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks', headers=headers, json=data)
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
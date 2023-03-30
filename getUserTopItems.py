import requests
import random

def get_user_top_items(access_token, time_range='short_term', limit=50):
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    params = {
        'time_range': time_range,
        'limit': limit,
        
    }
    response = requests.get('https://api.spotify.com/v1/me/top/tracks', headers=headers, params=params)
    tracks = response.json()['items']
    track_id = [track['id'] for track in tracks]
    random_id = random.sample(track_id, 4)
    if response.status_code == 200:
        return random_id
    else:
        print(response.status_code)
        return None
    
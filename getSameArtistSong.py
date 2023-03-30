import requests
import random

def getTopSong(id,token):
        url = "https://api.spotify.com/v1/artists/"+id+"/top-tracks/"
        print(url)
        headers = {
                "Authorization": "Bearer " + token
        }
        params = (
                ('market', 'IN'),
        )
        response = requests.get(url, headers=headers , params=params)
        tracks = response.json()['tracks']
        return random.sample(tracks, 1)

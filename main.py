from flask import Flask, render_template
from flask import Response, request, jsonify
import requests
import json
import base64
import time
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

@app.route("/")
def homepage():
    return render_template("index.html", title="Homepage")

# Spotify
client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')

# ChatGPT
api_key = os.environ.get('API_KEY')
organization_key = os.environ.get('ORGANIZATION_KEY')


client_creds = f"{client_id}:{client_secret}"
client_creds_b64 = base64.b64encode(client_creds.encode())
time_created = 0
access_token = ''

# 3540: 59 minutes

# send query to API Gateway
def get_token():
    token_api = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f"Basic {client_creds_b64.decode()}"
    }
    params = {
        'grant_type': 'client_credentials'
    }
    response = requests.post(token_api, headers=headers, data=params)
    access_token = json.loads(response.content)['access_token']
    return access_token, time.time()

def is_token_valid(access_token, time_created):
    if time.time() - time_created > 3540:
        return get_token()
    return access_token, time_created

def get_track_id(track_details, access_token, time_created):
    access_token, time_created = is_token_valid(access_token, time_created)

    search_url = 'https://api.spotify.com/v1/search'
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    params = {'q': track_details, 'type': 'track'}
    response = requests.get(search_url, headers=headers, params=params)
    track_id = response.json()['tracks']['items'][0]['id']
    return track_id

def get_track_spotify_url(track_id):
    track_spotify_url = 'https://open.spotify.com/track/' + track_id
    return track_spotify_url

def get_songs_chat_gpt(api_key, organization_key, content):
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer "+ api_key,
        "OpenAI-Organization": organization_key
    }
    body = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": content}],
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, json=body)
    content = response.json()['choices'][0]['message']['content']

    return content

def format_songs(songs_string):
    # Split the string by newlines to get a list of song strings
    songs_list = songs_string.split('\n')

    # Create a list of tuples containing the song title and artist name for each song
    songs_tuples = []
    for song in songs_list:
        # Replace any backslashes with an empty string
        song = song.replace("\\", "")
        # Extract the song title and artist from the string
        title = song.split('"')[1]
        artist = song.split('by ')[1].strip()
        # Create a tuple with the song title and artist, and append it to the list of tuples
        songs_tuples.append((title, artist))

    return songs_tuples

def get_track_details(songs_tuples):
    tracks = []
    for track in songs_tuples:
        track_details = track[0] + " by " + track[1]
        tracks.append(track_details)

    return tracks

def get_track_urls(tracks, access_token, time_created):
    tracks_urls = []

    for track in tracks:
        # get song id with name of song and artist
        track_id = get_track_id(track, access_token, time_created)
        # get the track spotify url for a song id
        track_spotify_url = get_track_spotify_url(track_id)
        tracks_urls.append((track, track_spotify_url))

    return tracks_urls

def print_results(tracks_urls):
    count = 1
    for track_url in tracks_urls:
        print(str(count) + ". " + track_url[0] + ": " + track_url[1])
        print()
        count += 1

@app.route('/get-spotify-url', methods=['POST'])
def get_spotify_url():
    # Get user input from the request object
    json_data = request.get_json()
    content = json_data['content']
    print(content)

    # Call the OpenAI API to generate a list of songs
    songs_string = get_songs_chat_gpt(api_key, organization_key, content)

    # Format the list of songs into a list of tuples containing song title and artist name
    songs_tuples = format_songs(songs_string)

    # Get the track details for each song
    track_details = get_track_details(songs_tuples)

    # Get the access token for the Spotify API
    access_token, time_created = get_token()

    # Get the Spotify URLs for the tracks in the list
    tracks_urls = get_track_urls(track_details, access_token, time_created)
    print(tracks_urls)
    # print the tracks_urls 
    print_results(tracks_urls)

    return jsonify(track_urls = tracks_urls)

if __name__ == "__main__":
    app.run(debug=True)
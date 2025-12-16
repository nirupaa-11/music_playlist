import requests
import base64
from flask import Flask,request,jsonify
from flask_cors import CORS 


client_id = 'client_id'
client_secret = 'client_secret'

auth_str = f"{client_id}:{client_secret}"
b64_auth_str = base64.b64encode(auth_str.encode()).decode()

url = "https://accounts.spotify.com/api/token"
header_aurth = {
    "Authorization": f"Basic {b64_auth_str}"
}
data = {
    "grant_type": "client_credentials"
}

response = requests.post(url, headers=header_aurth, data=data)
access_token = response.json()['access_token']

HEADERS={
    "Authorization":f"Bearer {access_token}"
}


SPOTIFY_BASE_URL = "https://api.spotify.com/v1"

saved_artist_name=None
saved_songs=[]
data_base=[]

def search_tracks(artist_name):
    search_url=f"{SPOTIFY_BASE_URL}/search"
    params={"q":artist_name,"type":"artist","limit":3}
    search_response=requests.get(search_url,headers=HEADERS,params=params)
    search_data=search_response.json()

    if search_response.status_code !=200:
        return {"error":"spotify API search failed "}
    if not search_data["artists"]["items"]:
        return {"error":"Artist not found"}
    artist_id=search_data["artists"]["items"][0]["id"]
    artist_real_name=search_data["artists"]["items"][0]["name"]

    top_tracks_url=f"{SPOTIFY_BASE_URL}/artists/{artist_id}/top-tracks"
    params={"country":"US"}
    top_tracks_response=requests.get(top_tracks_url,headers=HEADERS,params=params)
    top_tracks_data=top_tracks_response.json()

    if top_tracks_response.status_code != 200:
        return {"error":"Spotiy API call failed "}
    tracks=top_tracks_data["tracks"][:5]

    result={
        "artist": artist_real_name,
        "top_tracks":[
            {
                "track_name":track["name"],
                "album_name":track["album"]["name"],
                "spotify_url":track["external_urls"]["spotify"]
            }
            for track in tracks
        ]
    }
    return result 


app=Flask(__name__)
CORS(app)

@app.route("/artist",methods=["POST"])
def find_artist():
    global saved_artist_name
    data=request.get_json()
    saved_artist_name=data["artist"]
    return jsonify({"message":"artist name taken successfully"})

@app.route("/display",methods=["GET"])
def display_tracks():
    global saved_artist_name
    data=search_tracks(saved_artist_name)
    data_base.append(data)
    return jsonify(data)

@app.route("/song",methods=["POST"])
def save_songs():
    data=request.get_json()
    song=data["track_name"]
    saved_songs.append(song)
    return jsonify({"message":"song added successfully "})

@app.route("/saved",methods=["GET"])
def show_saved_songs():
    return jsonify(saved_songs)


app.run(debug=True)








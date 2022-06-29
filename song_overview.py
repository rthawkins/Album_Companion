import spotipy
import spotipy.util as util
import pandas as pd
from scipy import stats
from math import log
from wordcloud import WordCloud
from spotipy.oauth2 import SpotifyClientCredentials
import re
import locale
from decouple import config
import lyricsgenius
import requests
import numpy as np
import json
import textblob
from textblob import TextBlob 
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from bs4 import BeautifulSoup


id_ = config("spotify_id")
secret = config("spotify_secret")
genius_token = config('genius_token')
mg_usr = config('mg_usr')

ccm = SpotifyClientCredentials(client_id=id_, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=ccm)
genius = lyricsgenius.Genius(genius_token)
analyser = SentimentIntensityAnalyzer()

music_keys = {0:'C',1:'C#',2:'D',3:'D#',4:'E',5:'F',6:'F#',7:'G',8:'G#',9:'A',10:'A#',11:'B'}
mode = {0:'Minor',1:'Major'}

def high_low(df, new_col, source_col):
    criteria = [df[source_col].between(0, .2), df[source_col].between(.2, .4), df[source_col].between(.4, .6), df[source_col].between(.6, .8), df[source_col].between(.8, 1)]
    values = ['Very Low', 'Low', 'Neutral','High','Very High']
    df[new_col] = np.select(criteria, values, 0)
    
def pos_neg(df, new_col, source_col):
    criteria = [df[source_col].between(0, .2), df[source_col].between(.2, .4), df[source_col].between(.4, .6), df[source_col].between(.6, .8), df[source_col].between(.8, 1)]
    values = ['Very Negative', 'Negative', 'Neutral','Positive','Very Positive']
    df[new_col] = np.select(criteria, values, 0)

def clean_lyrics(lyrics):
    lyrics = lyrics.replace(r'mmm', '')
    lyrics = lyrics.replace(r'Lyrics for this song have yet to be released. Please check back once the song has been released.', '')
    lyrics = lyrics.replace(r'yeah', '')
    lyrics = lyrics.replace(r'Verse', '')
    lyrics = lyrics.replace(r'Intro', '')
    lyrics = lyrics.replace(r'Pre-Chorus', '')
    lyrics = lyrics.replace(r'Chorus', '')
    lyrics = lyrics.replace(r'Post-Chorus', '')
    lyrics = lyrics.replace(r'Guitar Solo', '')
    lyrics = lyrics.replace(r'Outro', '')
    lyrics = lyrics.replace(r'Bridge', '')
    lyrics = lyrics.replace(r'uh-huh', '')
    lyrics = lyrics.replace(r'whoa', '')
    lyrics = lyrics.replace(r'oh', '')
    lyrics = re.sub(r'\[.*\]', '', lyrics)
    lyrics = lyrics.replace(r'[', '')
    lyrics = lyrics.replace(r']', '')
    lyrics = lyrics.replace(r',', '')
    lyrics = lyrics.replace(r'?', '')
    lyrics = lyrics.replace(r'&', 'and')
    return lyrics

# https://github.com/salimzubair/lyric-sentiment
def get_lyric_sentiment(lyrics): 
    analysis = clean_lyrics(TextBlob(lyrics)) 
    return analysis.sentiment.polarity

# https://github.com/willamesoares/lyrics-crawler
def request_song_info(song_title, artist_name):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + genius_token}
    search_url = base_url + '/search?q=' + song_title + ' ' + artist_name
    response = requests.get(search_url, headers=headers)
    json = response.json()
    remote_song_info = None
    for hit in json['response']['hits']:
        if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
            remote_song_info = hit
            break
    return remote_song_info


def get_song_features(song_id):
    song_dict = sp.audio_features(song_id)
    df = pd.DataFrame(song_dict)
    df["song_key"] = df["key"].map(music_keys, na_action='ignore')
    df["mode"] = df['mode'].map(mode, na_action='ignore')
    df["title"] = sp.track(song_id)['name']
    df["title"] = df["title"][0].split("- Remaster", 1)[0]
    df["track"] = sp.track(song_id)['track_number']
    df["sp_id"] = sp.track(song_id)['id']
    df["album_id"] = sp.track(song_id)["album"]["id"]
    df["artist"] = sp.track(song_id)['artists'][0]['name']
    remote_song_info = request_song_info(df["title"][0], df["artist"][0])
    df["url"] = remote_song_info['result']['url']
    df["genius_songid"] = remote_song_info['result']['id']
    df["lyrics"] = get_lyrics(df["url"][0])
    df["lyr_valence"] = (get_lyric_sentiment(clean_lyrics(df["lyrics"][0])) + 1) / 2
    df["lyr_valence"] = round(df["lyr_valence"],3)
    df["mood"] = (df["lyr_valence"] + df["valence"]) / 2
    df["mood"] = round(df["mood"],3)
    df["energy"] = round(df["energy"],3)
    df["valence"] = round(df["valence"],3)
    df["tempo"] = round(df["tempo"],1)
    pos_neg(df, 'lyr_valence_des', 'lyr_valence')
    pos_neg(df, 'valence_des', 'valence')
    pos_neg(df, 'mood_des', 'mood')
    high_low(df, 'energy_des', 'energy')
    high_low(df, 'dance_des', 'danceability')
    song_dict = df.to_dict('records')[0]
    return song_dict

def search_song_id(query):
    track = sp.search(query, limit=1, type='track')
    sp_song_id = track["tracks"]["items"][0]["id"]
    return sp_song_id

def get_album_id(song_id):
    return sp.track(song_id)["album"]["id"]

def get_lyrics(url):
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics = html.select_one('div[class^="lyrics"], div[class^="SongPage__Section"]').get_text(separator="\n")
    # lyrics = html.find('div', class_='lyrics').get_text()
    split_string = lyrics.split("\nEmbed\nCancel", 1)
    lyrics = split_string[0]
    split_string = lyrics.split(" Lyrics\n", 1)
    lyrics = split_string[1]
    return lyrics


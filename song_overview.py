import spotipy
import spotipy.util as util
import pandas as pd
from scipy import stats
from math import log
from os import path
from wordcloud import WordCloud
from spotipy.oauth2 import SpotifyClientCredentials
import re
import lyricsgenius
import requests
import numpy as np
import json
import rh_config
from rh_config import token
from rh_config import sp
from rh_config import genius


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
    lyrics = lyrics.replace(r'yeah', '')
    lyrics = lyrics.replace(r'Verse', '')
    lyrics = lyrics.replace(r'Intro', '')
    lyrics = lyrics.replace(r'Pre-Chorus', '')
    lyrics = lyrics.replace(r'Chorus', '')
    lyrics = lyrics.replace(r'Post-Chorus', '')
    lyrics = lyrics.replace(r'Outro', '')
    lyrics = lyrics.replace(r'Bridge', '')
    lyrics = lyrics.replace(r'uh-huh', '')
    lyrics = lyrics.replace(r'whoa', '')
    lyrics = lyrics.replace(r'oh', '')
    lyrics = lyrics.replace(r'[', '')
    lyrics = lyrics.replace(r']', '')
    lyrics = lyrics.replace(r',', '')
    lyrics = lyrics.replace(r'?', '')
    lyrics = lyrics.replace(r'&', 'and')
    return lyrics

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyser = SentimentIntensityAnalyzer()

def sentiment_analyzer_scores(sentence):
    score = analyser.polarity_scores(sentence)
    return score['compound']


def request_song_info(song_title, artist_name):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + token}
    search_url = base_url + '/search'
    data = {'q': song_title + ' ' + artist_name}
    response = requests.get(search_url, data=data, headers=headers)
    return response


def get_song_features(song_id):
    song_dict = sp.audio_features(song_id)[0]
    df = pd.DataFrame([song_dict])
    df["key"] = df['key'].map(music_keys, na_action='ignore')
    df["mode"] = df['mode'].map(mode, na_action='ignore')
    df["title"] = sp.track(song_id)['name']
    df["track"] = sp.track(song_id)['track_number']
    df["sp_id"] = sp.track(song_id)['id']
    df["album_id"] = sp.track(song_id)["album"]["id"]
    df["artist"] = sp.track(song_id)['artists'][0]['name']
    title_search = genius.search_song(df["title"][0], df["artist"][0])
    df["lyrics"] = title_search.lyrics
    df["lyr_valence"] = (sentiment_analyzer_scores(clean_lyrics(title_search.lyrics)) + 1) / 2
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
    # criteria = [df['a'].between(1, 3), df['a'].between(4, 7), df['a'].between(8, 10)]
    # values = [1, 2, 3]
    # df['b'] = np.select(criteria, values, 0)
    response = request_song_info(df["title"][0], df["artist"][0])
    json_response = response.json()
    df["url"] = json_response['response']['hits'][0]['result']['url']
    df["genius_songid"] = json_response['response']['hits'][0]['result']['id']
    song_dict = df.to_dict('records')[0]
    return song_dict

def get_simple_features(song_id):
    song_dict = sp.audio_features(song_id)[0]
    df = pd.DataFrame([song_dict])
    df["key"] = df['key'].map(music_keys, na_action='ignore')
    df["mode"] = df['mode'].map(mode, na_action='ignore')
    df["track"] = sp.track(song_id)['track']
    df["title"] = sp.track(song_id)['name']
    df["sp_id"] = sp.track(song_id)['id']
    df["album_id"] = sp.track(song_id)["album"]["id"]
    df["artist"] = sp.track(song_id)['artists'][0]['name']
    df["energy"] = round(df["energy"],3)
    df["valence"] = round(df["valence"],3)
    df["tempo"] = round(df["tempo"],1)
    song_dict = df.to_dict('records')[0]
    return song_dict

def search_song_id(query):
    track = sp.search(query)
    sp_song_id = track["tracks"]["items"][0]["id"]
    return sp_song_id

def get_album_id(song_id):
    return sp.track(song_id)["album"]["id"]


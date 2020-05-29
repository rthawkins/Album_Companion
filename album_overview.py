# Return list of all ablum tracks w/attributes based on the album id
import pandas as pd 
import spotipy 
import json
import os
import pprint
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import mpld3
from scipy import stats
from pandas.io.json import json_normalize
import ipywidgets as widgets
from ipywidgets import interact, interact_manual
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import lyricsgenius
import re
import plotly.graph_objects as go
from song_overview import clean_lyrics
from song_overview import sentiment_analyzer_scores
import rh_config
from rh_config import token
from rh_config import sp
from rh_config import genius


# genius = lyricsgenius.Genius("***REMOVED***")
# sp = spotipy.Spotify() 
# from spotipy.oauth2 import SpotifyClientCredentials 
# cid ="***REMOVED***" 
# secret = "***REMOVED***" 
# client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret) 
# sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager) 
# sp.trace=False 
analyser = SentimentIntensityAnalyzer()


def analyze_album(album_id):
        tracks = []
        track_ids = []
        results = sp.album_tracks(album_id)
        tracks.extend(results['items'])
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
        for track in tracks:
            track_ids.append(track['id'])
        track_str = ','.join(map("'{0}'".format, track_ids)) 
        analysis_df = json_normalize(sp.audio_features(tracks=track_ids))
        tracks_df = json_normalize(sp.album_tracks(album_id)["items"])
        df = analysis_df.merge(tracks_df, on='id', how='inner')
        album_name = sp.album(album_id)["name"]
        album_name = clean_lyrics(album_name)
        release_date = sp.album(album_id)["release_date"]

        regex = '\[.*?\]'
        regex2 = '\-.*'

        titles = df["name"]
        artist = json_normalize(sp.album_tracks(album_id)["items"][0]["artists"])["name"][0]
        
        keys = {0:'C',1:'C#',2:'D',3:'D#',4:'E',5:'F',6:'F#',7:'G',8:'G#',9:'A',10:'A#',11:'B'}
        
        df["key"] = df['key'].map(keys, na_action='ignore')
        
        mode = {0:'Minor',1:'Major'}
        
        df["mode"] = df['mode'].map(mode, na_action='ignore')

        df["duration"] = (df["duration_ms_x"]/(1000*60))%60
    
        
        df['track'] = df['track_number']
        df = df.loc[df["disc_number"]==1]
        df = df.set_index('track_number')
        df = df[["name", "energy", "valence", "danceability", "loudness", "tempo", "key", "mode","time_signature","duration","id","track"]]
        df = df.rename(columns={"valence": "mus_valence"})
        
        energy_z = abs(stats.zscore(df["energy"]))
        valence_z = abs(stats.zscore(df["mus_valence"]))   
        dance_z = abs(stats.zscore(df["danceability"]))
        duration_z = abs(stats.zscore(df["duration"])) 
        loudness_z = abs(stats.zscore(df["loudness"])) 
        df["uniqueness"] = (energy_z + valence_z + dance_z + duration_z + loudness_z) / 5

        # print("Breakdown:")
        # print("")
        # print("Representative: " + df.loc[df['uniqueness'].idxmin()]["name"])
        # print("Unique: " + df.loc[df['uniqueness'].idxmax()]["name"])
        # print("Energetic: " + df.loc[df['energy'].idxmax()]["name"])
        # print("Slowest: " + df.loc[df['energy'].idxmin()]["name"])
        # print("Positive: " + df.loc[df['mood'].idxmax()]["name"])
        # print("Negative: " + df.loc[df['mood'].idxmin()]["name"])
        # print("Loudest: " + df.loc[df['loudness'].idxmax()]["name"])
        # print("Quietest: " + df.loc[df['loudness'].idxmin()]["name"])
        
        df = df.to_dict('records')
        df = json.dumps(df)
        return df
    
# Return list of all ablum tracks w/attributes based on the album id
import pandas as pd 
import spotipy 
import json
import locale
from decouple import config
import numpy as np
import mpld3
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from scipy import stats
from pandas.io.json import json_normalize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import lyricsgenius
import gensim
from gensim.summarization import keywords
import spacy
import nltk
from nltk import tokenize
import nrclex
from nrclex import NRCLex
from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('punkt')
stopwords = set(stopwords.words('english'))
from spacy.lang.en import English
nlp = English()
nlp.max_length = 10000000
from song_overview import clean_lyrics
from song_overview import get_lyric_sentiment
from song_overview import request_song_info
from song_overview import get_lyrics
import re
import requests
from bs4 import BeautifulSoup
from song_overview import high_low
from song_overview import pos_neg

id_ = config("spotify_id")
secret = config("spotify_secret")
genius_token = config('genius_token')
mg_usr = config('mg_usr')

token = util.prompt_for_user_token(username= mg_usr,
                           scope='user-read-currently-playing',
                           client_id= config("spotify_id"),
                           client_secret= config("spotify_secret"),
                           redirect_uri='https://album-companion.herokuapp.com/')

ccm = SpotifyClientCredentials(client_id=id_, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=ccm)
genius = lyricsgenius.Genius(genius_token)
analyser = SentimentIntensityAnalyzer()

def preprocess(text):
    # Create Doc object
    doc = nlp(text, disable=['ner', 'parser'])
    # Generate lemmas
    lemmas = [token.lemma_ for token in doc]
    # Remove stopwords and non-alphabetic characters
    a_lemmas = [lemma for lemma in lemmas 
            if lemma.isalpha() and lemma not in stopwords]
    
    return ' '.join(a_lemmas)

def return_keywords(texts):
    xkeywords = []
    values = keywords(text=preprocess(texts),split='\n',scores=True)
    for x in values[:10]:
        xkeywords.append(x[0])
    try:
        return xkeywords 
    except:
        return "no content"

def search_album(query):
    album_id = sp.search(query, limit=1, type='album')['albums']['items'][0]['id']
    return album_id

def sentiment_analyzer_scores(sentence):
    score = analyser.polarity_scores(sentence)
    return score['compound']

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
        analysis_json = sp.audio_features(tracks=track_ids)
        analysis_json = list(filter(None, analysis_json)) 
        tracks_json = sp.album_tracks(album_id)["items"]
        tracks_json = list(filter(None, tracks_json)) 
        analysis_df = json_normalize(analysis_json)
        tracks_df = json_normalize(tracks_json)
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
        df["album_id"] = album_id
        
        sent_score = []
        song_lyrics = []
        new_titles = []
        genius_url =[]
        genius_songid = []
        keywords = []
        affect_freq = []
        

        for title in df["name"]:
            try:
                title = re.sub(regex,'',title)
                title = re.sub(regex2,'',title)
                title = title.split("- Remaster", 1)[0]
                title = title.split("- Mono", 1)[0]
                new_titles.append(title)
                remote_song_info = request_song_info(title, artist)
                url = remote_song_info['result']['url']
                genius_url.append(url)
                genius_songid.append(remote_song_info['result']['id'])
                lyrics = get_lyrics(url)
                keywords.append(return_keywords(preprocess(clean_lyrics(lyrics))))
                sent_score.append(sentiment_analyzer_scores(lyrics))
                text_object = NRCLex(lyrics)
                affect_freq.append(text_object.affect_frequencies)
                song_lyrics.append(lyrics)
            except:
                sent_score.append(None)
                song_lyrics.append(None)
                keywords.append(None)
                affect_freq.append(None)
                genius_url.append(None)
                genius_songid.append(None)

        
        df['title'] = new_titles
        df["lyr_valence"] = sent_score
        df["lyr_valence"] = (df["lyr_valence"] + 1) / 2
        df['lyr_valence'] = df['lyr_valence'].fillna(df['valence'])
        df["lyr_valence"] = round(df["lyr_valence"],3)
        df["mood"] = (df["lyr_valence"] + df["valence"]) / 2
        df["mood"] = round(df["mood"],3)
        df["mood_discrep"] = df["valence"] - df["lyr_valence"]
        df["lyrics"] = song_lyrics
        pos_neg(df, 'lyr_valence_des', 'lyr_valence')
        pos_neg(df, 'valence_des', 'valence')
        pos_neg(df, 'mood_des', 'mood')
        high_low(df, 'energy_des', 'energy')
        high_low(df, 'dance_des', 'danceability')
        df["artist"] = artist
        df["album_name"] = album_name
        df["release_date"] = release_date
        df["sp_id"] = df["id"]
        df["genius_songid"] = genius_songid
        df["url"] = genius_url
        df['keywords'] = keywords
        df['affect_freq'] = affect_freq
        
        
        df = df.rename(columns={"valence": "mus_valence"})
        df = df.rename(columns={"external_urls.spotify": "external_urls_spotify"})
        
        energy_z = abs(stats.zscore(df["energy"]))
        valence_z = abs(stats.zscore(df["mus_valence"]))   
        dance_z = abs(stats.zscore(df["danceability"]))
        duration_z = abs(stats.zscore(df["duration"])) 
        loudness_z = abs(stats.zscore(df["loudness"])) 
        lyr_valence_z = abs(stats.zscore(df["lyr_valence"])) 
        df["uniqueness"] = (energy_z + valence_z + dance_z + duration_z + loudness_z + lyr_valence_z) / 6
        df = df[["title", "energy", "mus_valence", "lyr_valence", "mood", "danceability", "loudness", "tempo", "key", "mode","time_signature","duration","sp_id","track","lyrics","speechiness","acousticness","instrumentalness","liveness","artist","album_name","disc_number","explicit","external_urls_spotify","mood_discrep","release_date","uniqueness","lyr_valence_des","valence_des","mood_des","energy_des","dance_des","album_id","url","genius_songid", "keywords", "affect_freq"]]


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
        return df
    
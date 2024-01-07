import spotipy
import spotipy.util as util
import pandas as pd
import openai
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
import os
import openai
import urllib


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
    to_replace = ["mmm", "Lyrics for thissong have yet to be released. Please check back once the song has been released.",
                  "yeah", "Verse", "Intro", "Pre-Chorus", "Interlude", "Refrain", "Chorus", "Post-Chorus",
                  "Guitar Solo", "Outro", "Bridge", "uh-huh", "whoa", "oh"]
    for s in to_replace:
        lyrics = lyrics.replace(s, '')
    lyrics = re.sub(r'\[.*\]', '', lyrics)
    lyrics = lyrics.replace(r',', '')
    lyrics = lyrics.replace(r'?', '')
    lyrics = lyrics.replace(r'&', 'and')
    lyrics = re.sub(r"^.*?\n\n\n", "", lyrics, flags=re.DOTALL)
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
    # data = {'q': song_title + ' ' + artist_name}
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
    query =   df["artist"][0] + " " + df["title"][0]
    df["url"] = remote_song_info['result']['url']
    df["genius_songid"] = remote_song_info['result']['id']
    df["lyrics"] = genius_find_song_lyrics(query, genius_token)
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

# def get_lyrics(url):
#     page = requests.get(url)
#     html = BeautifulSoup(page.text, 'html.parser')
#     lyrics = html.select_one('div[class^="lyrics"], div[class^="SongPage__Section"]').get_text(separator="\n")
#     # lyrics = html.find('div', class_='lyrics').get_text()
#     split_string = lyrics.split("\nEmbed\nCancel", 1)
#     lyrics = split_string[0]
#     split_string = lyrics.split(" Lyrics\n", 1)
#     if len(split_string) < 2:
#         return ""
#     lyrics = split_string[1]
#     return lyrics

## Source https://github.com/ImranR98/AutoLyricize
def genius_find_song_lyrics(query, access_token):
    """
    Return song lyrics from Genius.com for the first song found using the provided search string.
    If not found, return None.
    Requires a Genius.com access token.
    """
    # Search Genius for the song using their API
    results = json.loads(requests.get(url="https://api.genius.com/search?q=" + urllib.parse.quote(query), headers={
        "Authorization": "Bearer " + access_token,
        "User-Agent": ""
    }).text)
    # If no hits, return None
    if len(results["response"]["hits"]) <= 0:
        return None
    # If the song has no URL or the artist or song name does not exist in the query, return None
    song = results["response"]["hits"][0]["result"]
    query_lower = query.lower()
    if song["url"] is None or query_lower.find(song["primary_artist"]["name"].lower()) < 0:
        return None
    # Scrape the song URL for the lyrics text
    page = requests.get(song["url"])
    html = BeautifulSoup(page.text, "html.parser")
    target_div = html.find("div", id="lyrics-root")
    # This ususally means the song is an instrumental (exists on the site and was found, but no lyrics)
    if target_div is None:
        lyrics = ["[Instrumental]"]
    else:
        lyrics = "\n".join(
            html.find("div", id="lyrics-root").strings).split("\n")[1:-2]
    # The extracted lyrics text is mangled, needs some processing before it is returned...
    indices = []
    for i, lyric in enumerate(lyrics):
        if lyric[0] == "[":
            indices.append(i)
    inserted = 0
    for i in indices:
        lyrics.insert(i+inserted, "")
        inserted += 1
    final_lyrics = []
    for i, lyric in enumerate(lyrics):
        if (i < (len(lyrics) - 1) and (lyrics[i+1] == ")" or lyrics[i+1] == "]")) or lyric == ")" or lyric == "]" or (i > 0 and lyrics[i-1].endswith(" ") or lyric.startswith(" ")):
            final_lyrics[len(final_lyrics) -
                         1] = final_lyrics[len(final_lyrics)-1] + lyric
        else:
            final_lyrics.append(lyric)
    return "[ti:" + song["title_with_featured"] + "]\n[ar:" + song["primary_artist"]["name"] + "]\n" + "\n".join(final_lyrics)

def song_interpreter(lyrics):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Completion.create(
    model="gpt-3.5-turbo-instruct",
    prompt="Lyrics:"+lyrics+"\n\nExtract these details:\n1) In three sentences, thoughtfully analyze the meaning of these lyrics in a paragraph, including an exploration of any symbols or metaphors. Do NOT refer to the song title - only provide an interpreation.\n2) In one word, describe the mood of these lyrics.\n3) List three themes of these lyrics, comma separated.\n\nResponse format: Analysis: <answer_1>|:|Mood: <answer_2>|:|Themes: <answer_3>\nResponse:",
    temperature=0.7,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    song_interpretation = response.choices[0].text
    return song_interpretation

# def song_themes(lyrics):
#     openai.api_key = os.getenv("OPENAI_API_KEY")
#     response = openai.Completion.create(
#     model="text-davinci-003",
#     prompt="Lyrics:"+lyrics+"\n\nList three themes in these lyrics (each theme comma separated):\n\n",
#     temperature=0.7,
#     max_tokens=64,
#     top_p=1,
#     frequency_penalty=0,
#     presence_penalty=0
#     )
#     song_themes = response.choices[0].text
#     return song_themes

# def song_mood_ai(lyrics):
#     openai.api_key = os.getenv("OPENAI_API_KEY")
#     response = openai.Completion.create(
#     model="text-davinci-003",
#     prompt="Lyrics:"+lyrics+"\n\nOne word that describes the mood of the lyrics:\n\n",
#     temperature=0.7,
#     max_tokens=64,
#     top_p=1,
#     frequency_penalty=0,
#     presence_penalty=0
#     )
#     song_mood_ai = response.choices[0].text
#     return song_mood_ai
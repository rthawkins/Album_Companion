# Return list of all ablum tracks w/attributes based on the album id
import pandas as pd 
import spotipy 
import json
import locale
from decouple import config
import numpy as np
import mpld3
import spotipy.util as util
import logging
log = logging.getLogger()
logging.basicConfig(level=logging.INFO)
import en_core_web_sm
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
from lexical_diversity import lex_div as ld
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

ccm = SpotifyClientCredentials(client_id=id_, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=ccm)
genius = lyricsgenius.Genius(genius_token)
analyser = SentimentIntensityAnalyzer()

# Determine text similarity to error search + error handling    
# https://www.datacamp.com/community/tutorials/fuzzy-string-python
def levenshtein_ratio_and_distance(s, t, ratio_calc = False):
    """ levenshtein_ratio_and_distance:
        Calculates levenshtein distance between two strings.
        If ratio_calc = True, the function computes the
        levenshtein distance ratio of similarity between two strings
        For all i and j, distance[i,j] will contain the Levenshtein
        distance between the first i characters of s and the
        first j characters of t
    """
    # Initialize matrix of zeros
    rows = len(s)+1
    cols = len(t)+1
    distance = np.zeros((rows,cols),dtype = int)

    # Populate matrix of zeros with the indeces of each character of both strings
    for i in range(1, rows):
        for k in range(1,cols):
            distance[i][0] = i
            distance[0][k] = k

    # Iterate over the matrix to compute the cost of deletions,insertions and/or substitutions    
    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0 # If the characters are the same in the two strings in a given position [i,j] then the cost is 0
            else:
                # In order to align the results with those of the Python Levenshtein package, if we choose to calculate the ratio
                # the cost of a substitution is 2. If we calculate just distance, then the cost of a substitution is 1.
                if ratio_calc == True:
                    cost = 2
                else:
                    cost = 1
            distance[row][col] = min(distance[row-1][col] + 1,      # Cost of deletions
                                 distance[row][col-1] + 1,          # Cost of insertions
                                 distance[row-1][col-1] + cost)     # Cost of substitutions
    if ratio_calc == True:
        # Computation of the Levenshtein Distance Ratio
        Ratio = ((len(s)+len(t)) - distance[row][col]) / (len(s)+len(t))
        return Ratio
    else:
        # print(distance) # Uncomment if you want to see the matrix showing how the algorithm computes the cost of deletions,
        # insertions and/or substitutions
        # This is the minimum number of edits needed to convert string a to string b
        return "The strings are {} edits away".format(distance[row][col])
    
# https://github.com/salimzubair/lyric-sentiment
def preprocess(text):
    # Create Doc object
    doc = nlp(text, disable=['ner', 'parser'])
    # Generate lemmas
    lemmas = [token.lemma_ for token in doc]
    # Remove stopwords and non-alphabetic characters
    a_lemmas = [lemma for lemma in lemmas 
            if lemma.isalpha() and lemma not in stopwords]
    
    return ' '.join(a_lemmas)

# https://github.com/salimzubair/lyric-sentiment
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

def search_metacritic(artist_name, album_name):
    
    query = f'{album_name}'
    url = f'https://www.metacritic.com/search/album/{query}/results'

    user_agent = {'User-agent': 'Mozilla/5.0'}
    response = requests.get(url, headers = user_agent)

    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all('h3', class_="product_title basic_stat")
    for result in results:
        if artist_name.lower().replace('-', ' ') in result.find('a')['href'].lower().replace('-', ' '):
            s_result = result.find('a')['href']
            break
            return s_result
    try:
        review_url = f'https://www.metacritic.com{s_result}'
        response = requests.get(review_url, headers = user_agent)
        soup = BeautifulSoup(response.text, 'html.parser')
        result = soup.find('div', class_="metascore_w xlarge album positive")
        score = result.find('span').text
        return int(score)
    except:
        print('Could not find.')
        None

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
        msttr = []
        lexical_depth = []
        cliche_word_perc = []
        cliche_total_count = []
        df["metacritic"] = search_metacritic(artist, album_name)
        

        for title in df["name"]:
            try:
                title = re.sub(regex2,'',title)
                title = title.split("- Remaster", 1)[0]
                title = title.split("[Remaster", 1)[0]
                title = title.split("(Remaster", 1)[0]
                title = title.split("- Mono", 1)[0]
                title = title.split("(Mono", 1)[0]
                title = title.split("[Mono", 1)[0]
                title = title.split("(with", 1)[0]
                title = title.split("[with", 1)[0]
                title = title.split("(featuring", 1)[0]
                title = title.split("- featuring", 1)[0]
                title = title.split("[featuring", 1)[0]
                new_titles.append(title)
                remote_song_info = request_song_info(title, artist)
                matching_artist = remote_song_info['result']['primary_artist']['name']
                matching_artist = matching_artist.lower()
                ratio = levenshtein_ratio_and_distance(artist.lower(),matching_artist,ratio_calc = True)
                if ratio > .6:
                    url = remote_song_info['result']['url']
                    genius_url.append(url)
                    genius_songid.append(str(remote_song_info['result']['id']))
                    lyrics = get_lyrics(url)
                    flt = ld.flemmatize(clean_lyrics(lyrics))
                    cliche_words = ['baby','love','boy','girl','feel','heart','happy','sad','cry']
                    excluded_words = ['\n','oh','verse','chorus','pre-chorus','bridge','woah','ya','la','nah','let','hoo','woo','thing','o','oo','whoa','yeah','guitar solo','haa','ayo','aah','interlude','1','2','3','4','5','','na','doo']
                    clean_flt = [x for x in flt if x.lower() not in excluded_words]
                    spacy_stopwords = list(spacy.lang.en.stop_words.STOP_WORDS)
                    depth = sum([1 for x in clean_flt if x.lower() not in spacy_stopwords])
                    cliche_count = sum([1 for x in clean_flt if x.lower() in cliche_words])
                    cliche_perc = cliche_count/depth
                    if depth >= 5: 
                        msttr.append(ld.msttr((clean_flt),window_length=100))
                        lexical_depth.append(depth)
                        cliche_word_perc.append(cliche_perc)
                        cliche_total_count.append(cliche_count)
                    else:
                        msttr.append(None)
                        lexical_depth.append(None)
                        cliche_word_perc.append(None)
                        cliche_total_count.append(None)
                    keywords.append(return_keywords(preprocess(clean_lyrics(lyrics))))
                    sent = sentiment_analyzer_scores(lyrics)
                    sent = round((sent + 1) / 2,3)
                    sent_score.append(sent)
                    text_object = NRCLex(lyrics)
                    affect_freq.append(text_object.affect_frequencies)
                    song_lyrics.append(lyrics)
                else:
                    sent_score.append(None)
                    song_lyrics.append(None)
                    keywords.append(None)
                    affect_freq.append(None)
                    genius_url.append(None)
                    genius_songid.append(None)
                    msttr.append(None)
                    lexical_depth.append(None)
                    cliche_word_perc.append(None)
                    cliche_total_count.append(None)
            except:
                sent_score.append(None)
                song_lyrics.append(None)
                keywords.append(None)
                affect_freq.append(None)
                genius_url.append(None)
                genius_songid.append(None)
                msttr.append(None)
                lexical_depth.append(None)
                cliche_word_perc.append(None)
                cliche_total_count.append(None)

        
        df['title'] = new_titles
        df["lyr_valence"] = sent_score   
        df['mood'] = np.where(df['lyr_valence'].isnull(), df['valence'], round((df["lyr_valence"] + df["valence"]) / 2,3) )
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
        df["lyr_valence"] = df["lyr_valence"].replace({np.nan: None}) 
        df["mood_discrep"] = df["mood_discrep"].replace({np.nan: None}) 
        df["lyr_valence_des"] = df["lyr_valence_des"].replace({'0': 'Not Found'}) 
        df['msttr'] = msttr
        df['lexical_depth'] = lexical_depth
        df['cliche_word_perc'] = cliche_word_perc
        df['cliche_total_words'] = cliche_total_count
        df["lexical_depth"] = df["lexical_depth"].replace({np.nan: None}) 
        df["msttr"] = df["msttr"].replace({np.nan: None}) 
        df["cliche_word_perc"] = df["cliche_word_perc"].replace({np.nan: None}) 
        df["cliche_total_words"] = df["cliche_total_words"].replace({np.nan: None}) 
        
        
        df = df.rename(columns={"valence": "mus_valence"})
        df = df.rename(columns={"external_urls.spotify": "external_urls_spotify"})
        
        energy_z = abs(stats.zscore(df["energy"]))
        mood_z = abs(stats.zscore(df["mood"]))   
        mus_valence_z = abs(stats.zscore(df["mus_valence"])) 
        dance_z = abs(stats.zscore(df["danceability"]))
        duration_z = abs(stats.zscore(df["duration"])) 
        loudness_z = abs(stats.zscore(df["loudness"])) 
        if None in df["msttr"].values:
            df["uniqueness"] = (energy_z + dance_z + duration_z + loudness_z + mood_z) / 5
        else:
            lex_diversity = abs(stats.zscore(df["msttr"])) 
            lyr_valence_z = abs(stats.zscore(df["lyr_valence"])) 
            df["uniqueness"] = (energy_z + dance_z + duration_z + loudness_z + lyr_valence_z + mus_valence_z + lex_diversity) / 7
        df = df[["title", "energy", "mus_valence", "lyr_valence", "mood", "danceability", "loudness", "tempo", "key", "mode","time_signature","duration","sp_id","track","lyrics","speechiness","acousticness","instrumentalness","liveness","artist","album_name","disc_number","explicit","external_urls_spotify","mood_discrep","release_date","uniqueness","lyr_valence_des","valence_des","mood_des","energy_des","dance_des","album_id","url","genius_songid", "keywords", "affect_freq","metacritic","msttr","lexical_depth","cliche_word_perc","cliche_total_words"]]
        
        df = df.to_dict('records')
        return df


def album_wordcloud(dict_name):
    dict_name = [ row for row in dict_name if row['lyrics'] is not None ]
    all_lyrics = ', '.join(d['lyrics'] for d in (dict_name))
    all_lyrics = clean_lyrics(all_lyrics)

    results = []

    nlp = en_core_web_sm.load()
    doc = nlp(all_lyrics)
    for token in doc:
        lyrics_overview ={'token_text':token.text, 
        'token_lemma':token.lemma_, 
        'token_pos':token.pos_, 
        'token_tag':token.tag_, 
        'token_dep':token.dep_,
        'token_shape':token.shape_, 
        'token_isalpha':token.is_alpha,
        'token_isstop':token.is_stop
        }
        results.append(lyrics_overview)
    df_lyrics = pd.DataFrame(results)
    excluded_words = ['\n','oh','verse','chorus','pre-chorus','bridge','woah','ya','la','nah','let','hoo','woo','thing','o','oo','whoa','yeah','guitar solo','haa','ayo','aah','interlude','yah','whoah']
    # Have to take out pronouns since Genius lyrics will sometimes contain the artist's name within the lyrics
    df_lyrics = df_lyrics.loc[df_lyrics["token_pos"]!='PROPN']
    df_lyrics = df_lyrics[df_lyrics["token_lemma"].apply(lambda x:x not in excluded_words)]
    # Remove irrelevant words
    df_lyrics = df_lyrics.loc[df_lyrics["token_isstop"]==False]
    df_lyrics = df_lyrics.loc[df_lyrics["token_pos"].isin(['NOUN','ADJ','ADV','VERB'])]
    df_lyrics = df_lyrics.loc[df_lyrics["token_isalpha"]==True]
    # Tranform into a dict with words and counts, sorted
    count_df = df_lyrics[["token_lemma"]].reset_index()
    count_df = count_df.groupby('token_lemma').count().reset_index()
    count_df.columns = ["word", "size"]
    # count_df = count_df.loc[count_df["size"]>1]
    count_df = count_df.sort_values('size',ascending=False)
    return count_df.to_dict('records')
        
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import lyricsgenius

token = util.prompt_for_user_token(username='rthawkins',
                           scope='user-read-currently-playing',
                           client_id='5a1378624b714bd49ac1f55eb755f579',
                           client_secret='7bb688c810ad47a68dae9a80aa384e75',
                           redirect_uri='https://album-companion.herokuapp.com/')

id_ ="5a1378624b714bd49ac1f55eb755f579" 
secret = "7bb688c810ad47a68dae9a80aa384e75" 
genius_token = "4I9B6Ee7dz4ZielbofNgpRCnnnkpfAbQSReqWo3K0Ge7UDG2JBy6rKc-B5Rbl6zf"

mg_usr = 'rthawkins'
mg_pwd = '=w=Qb2017!'
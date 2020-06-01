from flask import Flask, redirect, jsonify, render_template, request
from flask_pymongo import pymongo
import json
import logging
log = logging.getLogger()
logging.basicConfig(level=logging.INFO)
import song_overview
import album_overview
import os
from pymongo.errors import BulkWriteError
from bson import ObjectId
from song_overview import get_song_features
from song_overview import get_album_id
from song_overview import search_song_id
from album_overview import analyze_album
from album_overview import search_album
from rh_config import mg_pwd
from rh_config import mg_usr

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# usr = os.environ['rthawkins']
# pwd = os.environ['=w=Qb2017!']
# Need to secure first
client = pymongo.MongoClient(f"mongodb+srv://{mg_usr}:{mg_pwd}@cluster0-xcn4s.mongodb.net/test?retryWrites=true&w=majority")
db = client['albums_db']
collection = db['album_collection']


#################################################
# Flask Routes
#################################################


@app.route("/",methods=['GET', 'POST'])
def welcome():
    return render_template("index.html")

@app.route("/<song_id>")
def song_data(song_id):
    documents = collection.find({"sp_id": song_id})
    response = []
    for document in documents:
        document['_id'] = str(document['_id'])
        response.append(document)
    song_json = JSONEncoder().encode(response)
    song_dict = json.loads(song_json)[0]
    documents = collection.find({"album_id": song_dict['album_id']}).sort([("album_id", 1), ("track", 1)])
    response = []
    for document in documents:
        document['_id'] = str(document['_id'])
        response.append(document)
    album_new_data = JSONEncoder().encode(response)
    return render_template("view_track.html", song_dict=song_dict, album_new_data = album_new_data)

@app.route("/album/<album_id>")
def album_data(album_id):
    documents = collection.find({"album_id": album_id}).sort([("album_id", 1), ("track", 1)])
    response = []
    for document in documents:
        document['_id'] = str(document['_id'])
        response.append(document)
    result = JSONEncoder().encode(response)
    return result

@app.route('/search_result', methods=['POST'])
def search_result():
    album_search = search_album(request.form['album-search'])
    try: 
        if collection.find({"album_id": album_search}):
            documents = collection.find({"album_id": album_search}).sort([("album_id", 1), ("track", 1)])
            response = []
            for document in documents:
                document['_id'] = str(document['_id'])
                response.append(document)
            album_new_data = JSONEncoder().encode(response)
            song_dict = json.loads(album_new_data)[0]
        else:
            log.info("Could not find.")
            
    except:
        album = analyze_album(album_search)
        song_dict = album[0]
        collection.insert_many(album)
        album_new_data = JSONEncoder().encode(album)
    return render_template("view_track.html", song_dict=song_dict, album_new_data = album_new_data)
        
if __name__ == '__main__':
    app.run(debug=False)

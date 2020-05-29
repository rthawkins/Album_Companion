from flask import Flask, redirect, jsonify, render_template, request
import json
import logging
import song_overview 
import album_overview 

from bson import ObjectId
from bson import json_util
from flask.json import JSONEncoder


#################################################
# Flask Setup
#################################################
app = Flask(__name__)
app.json_encoder = JSONEncoder()

#################################################
# Flask Routes
#################################################


@app.route("/",methods=['GET', 'POST'])
def welcome():
    return render_template("index.html")

@app.route("/<song_id>")
def song_data(song_id):
    song_dict = song_overview.get_song_features(song_id)
    album_new_data = album_overview.analyze_album(song_overview.get_album_id(song_id))
    return render_template("view_track.html", song_dict=song_dict, album_new_data = album_new_data)

@app.route("/album/<album_id>")
def album_data(album_id):
    album_new_data = album_overview.analyze_album(album_id)
    return album_new_data

@app.route('/search_result', methods=['POST'])
def search_result():
    selected_song = song_overview.search_song_id(request.form['track-search'])
    song_dict = song_overview.get_song_features(selected_song)
    album_new_data = album_overview.analyze_album(song_overview.get_album_id(selected_song))
    return render_template("view_track.html", song_dict=song_dict, album_new_data = album_new_data)

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, send_from_directory
from classes.extract import *
from os import environ
from functions import *

app = Flask(__name__)


@app.route("/", methods=['GET'])
def hello():
    return render_template('index.html', error='')


@app.route('/extract', methods=['GET'])
def extract():
    playlistName = get_arguments('playlistName')
    playlistGenre = get_arguments('playlistGenre')
    playlistURL = get_arguments('playlistURL')

    print(playlistName)
    print(playlistURL)

    if playlistName == '' or playlistURL == '':
        return render_template('index.html', error='Please enter playlist url and playlist name')
    else:
        extractedData = Extract(playlistName, playlistGenre, playlistURL)
        if extractedData.dataJson == {}:
            return render_template('index.html', error='Please enter a valid url')
        else:
            return extractedData.dataJson


if __name__ == '__main__':
  app.run(debug = True, host = '0.0.0.0', port=environ.get("PORT", 4000))
from flask import Flask, render_template
from classes.extract import *
from os import environ
from functions import *

app = Flask(__name__)

@app.route("/", methods=['GET'])
def hello():
    return render_template('index.html')

@app.route('/extract', methods=['GET'])
def extract():
    playlistName = get_arguments('playlistName')
    playlistGenre = get_arguments('playlistGenre')
    playlistURL = get_arguments('playlistURL')
    fileName = get_arguments('fileName')

    extractedData = Extract(playlistName, playlistGenre, playlistURL, fileName)

    if extractedData.dataJson == {}:
        return render_template('index.html')
    else:
        return extractedData.dataJson

if __name__ == '__main__':
  app.run(debug = True, host = '0.0.0.0', port=environ.get("PORT", 4000))
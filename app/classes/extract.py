import requests
from time import sleep
import pandas as pd
from flask import jsonify

from variables import *
from variablesPriv import *

class Extract():
    '''
    This class contains all the necessary data to extract all the tracks from a given playlist, store the 
    track details, and save it into a csv file.
    '''
    # Track features that we can import using the same syntax
    trackFeatureList = trackFeatureList   # Track name and track popularity
    artistFeatureList = artistFeatureList   # Artist genres and artist popularity
    audioFeatureList = audioFeatureList   # Audio features 

    CLIENT_ID = CLIENT_ID   # Client id, personal credential
    CLIENT_SECRET = CLIENT_SECRET   # Client secret, personal credential

    AUTH_URL = AUTH_URL   # Authorisation URL
    BASE_URL = BASE_URL   # Base URL of all Spotify API endpoints

    offset = 0   # The offset is set to 0 and it will be increased later

    trackData = {}   # Empty dictionary where all the data will be stored


    def __init__(self, playlistName, playlistGenre, playlistURL):
        '''
        This function will initiate the clase, given the following playlist elements:
            · name
            · genre
            · link
            · name
        It will create the necessary authentifications, extract all the data, 
        store it in dictionaries, and save it as csv
        '''
        self.playlistName = playlistName
        self.playlistGenre = playlistGenre
        self.playlistURL = playlistURL

        self.getPlaylistID()   # Transform the playlist link to get the id
        self.modEmptyGenre()   # Modify the genre if empty
        self.apiResponse()   # Create the authentification to access data
        self.getResponseCode()
        if self.statusCode == 200:
            self.getAllTracks()   # Access each of the tracks of the playlist
            self.extractAllData()   # Extract all the data which will be stored
            self.jsonifyDict()
        else:
            self.dataJson = {}
        # self.dict_to_df()   # Transform the dictionary into a dataframe
        # self.df_to_csv()   # Save the dataframe as a csv file
        

    def getPlaylistID(self):
        '''
        This functions transforms the playlist link to get the id
        '''
        self.playlistID = self.playlistURL.split("/")[-1].split("?")[0] 


    def modEmptyGenre(self):
        '''
        This functions sets the genre as undefined, in case it's empty.
        '''
        if self.playlistGenre == '':
            self.playlistGenre = 'undefined' 


    def apiResponse(self):
        '''
        This function will create the personalised headers to get data from the API
        Needed personal variables: client_id, client_secret
        '''
        # create the response from the API
        authResponse = requests.post(self.AUTH_URL, {'grant_type': 'client_credentials',
                                                     'client_id': self.CLIENT_ID,
                                                     'client_secret': self.CLIENT_SECRET,})

        authResponseData = authResponse.json()   # convert the response to JSON

        accessToken = authResponseData['access_token']   # save the access token

        self.headers = {'Authorization': 'Bearer {token}'.format(token=accessToken)}   # Save the headers


    def getResponseCode(self):
        self.playlist100 = requests.get(self.BASE_URL + 'playlists/' + self.playlistID + '/tracks',    
                                headers=self.headers, params={'offset':self.offset})
        self.statusCode = self.playlist100.status_code


    def getAllTracks(self):
        '''
        This function will get a list with all the tracks from the given playlist
        '''
        playlist100Dict = self.playlist100.json()   # Transform the result into a dictionary

        self.playlistItems = playlist100Dict['items']   # Keep just the list with the items values

        # This loop will iterate over all the tracks from the playlist while the offset (starting
        # from 0) is smaller than the total number of tracks, which we can find under the key 'total'
        while self.offset < playlist100Dict['total']:  

            self.offset += 100   # adding 100 to the offset will get the next 100 tracks and we will do a new call

            playlist100 = requests.get(BASE_URL + 'playlists/' + self.playlistID + '/tracks', 
                                    headers=self.headers, params={'offset':self.offset})

            playlist100Dict = playlist100.json()   # add the result to a dictionary

            playlistItems100 = playlist100Dict['items']   # extract the values under items

            for elem in playlistItems100:   # append the new values to the previous list
                self.playlistItems.append(elem)


    def apiCall(self, url_string, url_id):
        '''
        This function will do individual calls to the API
        '''
        self.apiData = requests.get(self.BASE_URL + url_string + '/' + url_id, headers=self.headers)

        self.apiData = self.apiData.json()


    def defineTrackID(self):
        '''
        This function will modify the track name, call the api and return the id of the track
        '''
        self.track_id = self.track['track']['uri']   # Obtain the track id from the track uri

        self.track_id = self.track_id.replace('spotify:track:', '')   # Remove unnecesary characters from the id

        self.trackData[self.track_id] = {}   # Create a new dictionary key with the track id


    def playlistData(self):
        '''
        This function will store the playlist url and name in order to keep the information next to the track
        '''
        self.individualTrackFeatures['playlist_url'] = self.playlistURL   # Store the playlist link 
        self.individualTrackFeatures['playlist_name'] = self.playlistName   # Store the playlist name 


    def trackMainFeatures(self):
        '''
        This function will iterate over the main track features and extract them into a dictionary
        '''
        for feature in self.trackFeatureList:   # loop over the track main features and store them
            try:
                featureData = self.track['track'][feature]
                feature = 'track_' + feature
                self.individualTrackFeatures[feature] = featureData
            except:
                self.individualTrackFeatures[feature] = None
            
        # Artist name
        try:
            artistName = self.track['track']['artists'][0]['name']   # Extract and store the artist name
            self.individualTrackFeatures['artist_name'] = artistName 
        except:
            self.individualTrackFeatures['artist_name'] = None

        # Album name
        try:
            album = self.track['track']["album"]["name"]   # Extract and store the album name
            self.individualTrackFeatures['album'] = album
        except: 
            self.individualTrackFeatures['album'] = None 

        # Album cover
        try:
            albumCover = self.track['track']["album"]["images"][0]['url']   # Extract and store the album cover
            self.individualTrackFeatures['album_cover'] = albumCover
        except:
            self.individualTrackFeatures['album_cover'] = None

        self.artist_id = self.track['track']["artists"][0]["uri"]   # Extract the id of the artist 
        self.artist_id = self.artist_id.replace('spotify:artist:', '')

    
    def extractArtistFeatures(self):
        '''
        This function will iterate over the main artist features and extract them into a dictionary
        '''
        for feature in self.artistFeatureList:   # Loop over the artist main features, extract and store the data
            try:
                featureData = self.apiData[feature]
                feature = 'artist_' + feature   # Transform the name of the feature to be albe to identify the data   
                self.individualTrackFeatures[feature] = featureData
            except:
                self.individualTrackFeatures[feature] = None 


    def extractAudioFeatures(self):
        '''
        This function will iterate over all the audio features and extract them into a dictionary
        '''
        for feature in self.audioFeatureList:   # Loop over the audio feature list, extract and store the data
            try:
                featureData = self.apiData[feature] 
                self.individualTrackFeatures[feature] = featureData
            except:
                self.individualTrackFeatures[feature] = None 


    def extractAllData(self):
        '''
        This function will loop over all the tracks, extract all their data, and store it into a nested dictionary
        Since we have added dictionaries into track_list, and every dictionary has 100 tracks, 
        we need to iterate over each of them
        '''
        for index, self.track in enumerate(self.playlistItems):   # This loop will iterate over the tracks in the dictionary and get the information

            self.individualTrackFeatures = {}   # Empty dictionary to store data of every individual track
            
            try:
                self.defineTrackID()   # Extract the track ID and create the dictionary key  

                self.playlistData()   # Store playlist url and name

                self.trackMainFeatures()   # Extract the track main features, and store the artist id

                self.apiCall('artists', self.artist_id)   # Access the artist features using the artist id

                self.extractArtistFeatures()   # Extract the artist main features

                self.apiCall('audio-features', self.track_id)   # Access the audio features using the track id
                        
                self.extractAudioFeatures()   # Extract the audio features

                self.individualTrackFeatures['genre'] = self.playlistGenre   # Add the genre of the list to the dict 

                self.dict_into_dict()   # Add the data into the nested dictionary, under the specific track id key

                sleep(0.1)

            except:
                continue

    
    def dict_into_dict(self):
        '''
        This function will add the audio features in a nested dictionary, under the track_id 
        '''
        self.trackData[self.track_id] = self.individualTrackFeatures

    
    def jsonifyDict(self):
        '''
        This function will transform the resulting dictionary into a json file
        '''
        self.dataJson = jsonify(self.trackData)

    
    def dict_to_df(self):
        '''
        This function will transform the resulting dictionary into a dataframe
        '''
        self.trackDataDf = pd.DataFrame.from_dict(self.trackData, orient='index')


    def df_to_csv(self):
        '''
        This function will save the dataframe as a csv file
        '''
        path = self.fileName + '.csv'
        self.trackDataDf.to_csv(path)
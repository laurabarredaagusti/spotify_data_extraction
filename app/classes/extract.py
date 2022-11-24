import requests
from time import sleep
import pandas as pd

from variables import *
from variablesPriv import *

class Extract():
    '''
    This class contains all the necessary data to extract all the tracks from a given playlist, store the 
    track details, and save it into a csv file.
    '''
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
        self.authenticate()   # Create the authentification to access data
        self.playlist = self.apiCall(f'playlists/{self.playlistID}/tracks', {'offset':self.offset})
        if self.playlist.status_code == 200:
            self.getAllTracks(self.playlist.json())   # Access each of the tracks of the playlist
            self.extractAllData()   # Extract all the data which will be stored
        

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


    def authenticate(self):
        '''
        This function will create the personalised headers to get data from the API
        Needed personal variables: client_id, client_secret
        '''
        # create the response from the API
        authResponse = requests.post(AUTH_URL, {'grant_type': 'client_credentials',
                                                     'client_id': CLIENT_ID,
                                                     'client_secret': CLIENT_SECRET,})

        authResponseData = authResponse.json()   # convert the response to JSON

        self.headers = {'Authorization': 'Bearer {token}'.format(token=authResponseData['access_token'])}   # Save the headers


    def apiCall(self, url_string, parameters=None):
        '''
        This function will do individual calls to the API
        '''
        return requests.get(BASE_URL + url_string, headers=self.headers, params=parameters)


    def getAllTracks(self, playlist):
        '''
        This function will get a list with all the tracks from the given playlist
        '''
        self.playlistItems = playlist['items']   # Keep just the list with the items values

        # This loop will iterate over all the tracks from the playlist while the offset (starting
        # from 0) is smaller than the total number of tracks, which we can find under the key 'total'
        while self.offset < playlist['total']:  

            self.offset += 100   # adding 100 to the offset will get the next 100 tracks and we will do a new call

            playlist = self.apiCall(f'playlists/{self.playlistID}/tracks', {'offset':self.offset}).json()   # add the result to a dictionary

            for elem in playlist['items']:   # append the new values to the previous list
                self.playlistItems.append(elem)


    def defineTrackID(self, track):
        '''
        This function will modify the track name, call the api and return the id of the track
        '''
        track_id = track['track']['uri']   # Obtain the track id from the track uri

        track_id = track_id.replace('spotify:track:', '')   # Remove unnecesary characters from the id

        self.trackData[track_id] = {}   # Create a new dictionary key with the track id

        return track_id


    def addPlaylistData(self, individualTrackFeatures):
        '''
        This function will store the playlist url and name in order to keep the information next to the track
        '''
        individualTrackFeatures['playlist_url'] = self.playlistURL   # Store the playlist link 
        individualTrackFeatures['playlist_name'] = self.playlistName   # Store the playlist name
        individualTrackFeatures['genre'] = self.playlistGenre

        return individualTrackFeatures


    def addTrackMainFeatures(self, individualTrackFeatures, track):
        '''
        This function will iterate over the main track features and extract them into a dictionary
        '''
        for feature in TRACK_FEATURE_LIST:   # loop over the track main features and store them
            try:
                individualTrackFeatures[f'track_{feature}'] = track['track'][feature]
            except:
                individualTrackFeatures[feature] = None
            
        # Artist name
        try:
            individualTrackFeatures['artist_name'] = track['track']['artists'][0]['name']   # Extract and store the artist name 
        except:
            individualTrackFeatures['artist_name'] = None

        # Album name
        try:
            individualTrackFeatures['album'] = track['track']["album"]["name"]
        except: 
            individualTrackFeatures['album'] = None 

        # Album cover
        try:
            individualTrackFeatures['album_cover'] = track['track']["album"]["images"][0]['url']
        except:
            individualTrackFeatures['album_cover'] = None

        artist_id = track['track']["artists"][0]["uri"]   # Extract the id of the artist 
        return individualTrackFeatures, artist_id.replace('spotify:artist:', '')

    
    def addArtistFeatures(self, artistData, individualTrackFeatures):
        '''
        This function will iterate over the main artist features and extract them into a dictionary
        '''
        for feature in ARTIST_FEATURE_LIST:   # Loop over the artist main features, extract and store the data
            try:
                individualTrackFeatures[f'artist_{feature}'] = artistData[feature]
            except:
                individualTrackFeatures[feature] = None

        return individualTrackFeatures


    def addAudioFeatures(self, audioFeatures, individualTrackFeatures):
        '''
        This function will iterate over all the audio features and extract them into a dictionary
        '''
        for feature in AUDIO_FEATURES_LIST:   # Loop over the audio feature list, extract and store the data
            try:
                individualTrackFeatures[feature] = audioFeatures[feature] 
            except:
                individualTrackFeatures[feature] = None
        
        return individualTrackFeatures


    def extractAllData(self):
        '''
        This function will loop over all the tracks, extract all their data, and store it into a nested dictionary
        Since we have added dictionaries into track_list, and every dictionary has 100 tracks, 
        we need to iterate over each of them
        '''
        for track in self.playlistItems:   # This loop will iterate over the tracks in the dictionary and get the information

            try:
                track_id = self.defineTrackID(track)   # Extract the track ID and create the dictionary key  

                individualTrackFeatures = self.addPlaylistData({})   # Store playlist url and name

                individualTrackFeatures, artist_id = self.addTrackMainFeatures(individualTrackFeatures, track)   # Extract the track main features, and store the artist id
                
                individualTrackFeatures = self.addArtistFeatures(self.apiCall(f'artists/{artist_id}').json(), individualTrackFeatures)   # Extract the artist main features
                    
                individualTrackFeatures = self.addAudioFeatures(self.apiCall(f'audio-features/{track_id}').json(), individualTrackFeatures)   # Extract the audio features

                self.trackData[track_id] = individualTrackFeatures

                sleep(0.1)

            except:
                continue
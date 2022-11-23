import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials   # This will allow us to create credentials
from variables import *

class Extract_100():
    '''
    This class contains all the necessary data to extract the 100 first tracks from a given playlist, store the 
    track details, and save it into a csv file.
    '''
    # Track features that we can import using the same syntax
    track_features_list = track_features_list   # Track name and track popularity

    artist_features_list = artist_features_list   # Artist genres and artist popularity

    audio_features_list = audio_features_list   # Audio features

    CLIENT_ID = CLIENT_ID   # client id, personal credential
    CLIENT_SECRET = CLIENT_SECRET   # client secret, personal credential

    track_data = {}   # Empty dictionary where all the data will be stored

    def __init__(self):
        '''
        This function will initiate the clase, given the following playlist elements:
            · name
            · genre
            · link
            · name
        It will create the necessary authentifications, extract all the data, store it in dictionaries, and save it as csv
        '''
        self.get_playlist_data()
        self.create_authentification()   # Create the authentification to access data
        self.extract_all_data()   # Extract all the data which will be stored
        self.dict_to_df()   # Transform the dictionary into a dataframe
        self.df_to_csv()   # Save the dataframe as a csv file


    def get_playlist_data(self):
        self.playlist_name = input('Enter the name of the playlist: ')
        self.playlist_genre = input('Enter the genre of the playlist: ')
        self.playlist_link = input('Enter the playlist url: ')
        self.file_name = input('Enter the name of the resulting file: ')
        # Transform the playlist link to get the id
        self.playlist_id = self.playlist_link.split("/")[-1].split("?")[0]  
        

    def create_authentification(self):
        '''
        This function will create the authentification and allow us to access the track feautures
        '''
        client_credentials_manager = SpotifyClientCredentials(client_id=self.CLIENT_ID, client_secret=self.CLIENT_SECRET)
        self.sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)


    def define_track_id(self):
        '''
        This function will modify the track name, call the api and return the id of the track
        '''
        self.track_id = self.track['track']['id']   # Obtain the track id from the track uri
        self.track_data[self.track_id] = {}   # Create a new dictionary key with the track id


    def store_playlist_data(self):
        '''
        This function will store the playlist url and name in order to keep the information next to the track
        '''
        self.all_track_features['playlist_url'] = self.playlist_link   # Store the playlist link 
        self.all_track_features['playlist_name'] = self.playlist_name   # Store the playlist name 


    def extract_track_main_features(self):
        '''
        This function will iterate over the main track features and extract them into a dictionary
        '''
        for feature in self.track_features_list:   # loop over the track main features and store them
            try:
                feature_data = self.track['track'][feature]
                feature = 'track_' + feature
                self.all_track_features[feature] = feature_data
            except:
                self.all_track_features[feature] = None
            
        # Artist name
        try:
            artist_name = self.track['track']['artists'][0]['name']   # Extract and store the artist name
            self.all_track_features['artist_name'] = artist_name 
        except:
            self.all_track_features['artist_name'] = None

        # Album name
        try:
            album = self.track['track']["album"]["name"]   # Extract and store the album name
            self.all_track_features['album'] = album
        except: 
            self.all_track_features['album'] = None 

        # Album cover
        try:
            album_cover = self.track['track']["album"]["images"][0]['url']   # Extract and store the album cover
            self.all_track_features['album_cover'] = album_cover
        except:
            self.all_track_features['album_cover'] = None

        self.artist_id = self.track['track']["artists"][0]["uri"]   # Extract the id of the artist 
        self.artist_id = self.artist_id.replace('spotify:artist:', '')

    
    def extract_artist_features(self):
        '''
        This function will iterate over the main artist features and extract them into a dictionary
        '''
        for feature in self.artist_features_list:   # Loop over the artist main features, extract and store the data
            try:
                feature_data = self.track[feature]
                feature = 'artist_' + feature   # Transform the name of the feature to be albe to identify the data   
                self.all_track_features[feature] = feature_data
            except:
                self.all_track_features[feature] = None 


    def extract_track_audio_features(self):
        '''
        This function will iterate over all the audio features and extract them into a dictionary
        '''
        for feature in self.audio_features_list:   # Loop over the audio feature list, extract and store the data
            try:
                feature_data = self.track[0][feature] 
                self.all_track_features[feature] = feature_data
            except:
                self.all_track_features[feature] = None 


    def extract_all_data(self):
        '''
        This function will loop over all the tracks, extract all their data, and store it into a nested dictionary
        '''
        for self.track in self.sp.playlist_tracks(self.playlist_id)["items"]:   # Loop over the 100 first tracks

            self.all_track_features = {}   # Empty dictionary to store data of every individual track

            self.define_track_id()   # Extract the track ID and create the dictionary key

            self.store_playlist_data()   # Store playlist url and name

            self.extract_track_main_features()   # Extract the track main features, and store the artist id

            self.track = self.sp.artist(self.artist_id)   # Access the artist features using the artist id

            self.extract_artist_features()   # Extract the artist main features

            self.track = self.sp.audio_features(self.track_id)   # Access the audio features using the track id
                    
            self.extract_track_audio_features()   # Extract the audio features

            self.dict_into_dict()   # Add the data into the nested dictionary, under the specific track id key

    
    def dict_into_dict(self):
        '''
        This function will add the audio features in a nested dictionary, under the track_id 
        '''
        self.track_data[self.track_id] = self.all_track_features

    
    def dict_to_df(self):
        '''
        This function will transform the resulting dictionary into a dataframe
        '''
        self.track_data_df = pd.DataFrame.from_dict(self.track_data, orient='index')


    def df_to_csv(self):
        '''
        This function will save the dataframe as a csv file
        '''
        path = '../../../genre_prediction/src/data/raw_data/individual_playlist/' + self.file_name + '.csv'   # Add the path information to the file name
        self.track_data_df.to_csv(path)
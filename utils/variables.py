track_features_list = ['name', 'popularity']   # Track name and track popularity

artist_features_list = ['genres', 'popularity']   # Artist genres and artist popularity

audio_features_list = ['danceability', 'energy', 'key', 'loudness', 'mode',  
                       'speechiness', 'acousticness', 'instrumentalness', 'liveness',   # Audio features  
                       'valence', 'tempo', 'duration_ms', 'time_signature'] 

CLIENT_ID = 'b3efc4982a5a4c7197f979d08087128d'   # client id, personal credential
CLIENT_SECRET = '3cd6cc8bdf114d9a97be07ad12024683'   # client secret, personal credential    

AUTH_URL = 'https://accounts.spotify.com/api/token'   # Authorisation URL

BASE_URL = 'https://api.spotify.com/v1/'   # Base URL of all Spotify API endpoints
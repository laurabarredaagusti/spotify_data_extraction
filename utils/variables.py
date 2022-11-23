track_features_list = ['name', 'popularity']   # Track name and track popularity

artist_features_list = ['genres', 'popularity']   # Artist genres and artist popularity

audio_features_list = ['danceability', 'energy', 'key', 'loudness', 'mode',  
                       'speechiness', 'acousticness', 'instrumentalness', 'liveness',   # Audio features  
                       'valence', 'tempo', 'duration_ms', 'time_signature']  

AUTH_URL = 'https://accounts.spotify.com/api/token'   # Authorisation URL

BASE_URL = 'https://api.spotify.com/v1/'   # Base URL of all Spotify API endpoints
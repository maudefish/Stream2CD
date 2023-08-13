from flask import Flask, request, redirect, session
import json
import webbrowser
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os #to interface with blackhole

current_dir = os.getcwd()


load_dotenv(dotenv_path='./config.env')
blackhole_id = "BlackHole 2ch"
client_id = os.environ.get('SPOTIPY_CLIENT_ID')
client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
redirect_uri = 'http://localhost:8888/callback/'
username = os.environ.get('SPOTIPY_USERNAME')

# ... rest of the Flask setup ...
# Authenticate
app = Flask(__name__)

# Endpoint to start the Spotify login process
@app.route('/')
def index():
    return '''
        <form action="/login" method="post">
            Please enter the full link of the playlist:
            <input type="text" name="playlist_url">
            <input type="submit">
        </form>
    '''
app.secret_key = 'your_secret_key' # You should set this to a random value

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        playlist_url = request.form['playlist_url']
        playlist_id = playlist_url.split("/")[-1].split("?")[0]
        print(f'Setting playlist_id: {playlist_id}') # Debugging
        session['playlist_id'] = playlist_id
    auth_url = SpotifyOAuth(client_id=client_id,
                            client_secret=client_secret,
                            redirect_uri="http://localhost:8888/callback/",
                            scope='playlist-modify-public playlist-modify-private playlist-read-private user-read-playback-state user-modify-playback-state app-remote-control').get_authorize_url()
    return redirect(auth_url)

# Callback to handle the response from Spotify
@app.route('/callback/')
def callback():
    if 'playlist_id' not in session:
        return redirect('/') # Redirect back to login if playlist_id is missing
    playlist_id = session['playlist_id']
    auth_manager = SpotifyOAuth(client_id=client_id,
                                client_secret=client_secret,
                                redirect_uri="http://localhost:8888/callback/",
                                scope='playlist-modify-public playlist-modify-private playlist-read-private user-read-playback-state user-modify-playback-state app-remote-control')
    token_info = auth_manager.get_access_token(request.args['code'])
    access_token = token_info['access_token']

    # Here you can use the access token to create a Spotipy object and proceed with your logic
    sp = spotipy.Spotify(auth=access_token)
    playlist_id = session['playlist_id'] # Retrieve from session
    with open('auth_info.json', 'w') as f:
        json.dump({'access_token': access_token, 'playlist_id': playlist_id}, f)

    return "Logged in successfully. You can now run the main script."


    # For now, return a success message
    return "Logged in successfully."

if __name__ == '__main__':
    port = 8888
    webbrowser.open(f'http://127.0.0.1:{port}/')
    app.run(port=port)

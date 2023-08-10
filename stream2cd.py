import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os #to interface with blackhole
import subprocess
import time

current_dir = os.getcwd()

load_dotenv(dotenv_path='./config.env')

def get_volume():
    return int(subprocess.getoutput('osascript -e "output volume of (get volume settings)"'))

def set_volume(level):
    command = "osascript -e 'set volume output volume {}'".format(level)
    subprocess.run(command, shell=True)

def sanitize_filename(filename):
    invalid_characters = '<>:"/\\|?*'
    for char in invalid_characters:
        filename = filename.replace(char, '_')
    return filename

def sanitize_folder_name(name):
    return "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).strip()

blackhole_id = "BlackHole 2ch"
# blackhole_id = "blackhole+headphones"
# Replace with your values
client_id = os.environ.get('SPOTIPY_CLIENT_ID')
print(client_id)
client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
redirect_uri = 'http://localhost:8888/callback/'
username = os.environ.get('SPOTIPY_USERNAME')
playlist_id = os.environ.get('PLAYLIST_ID')

# Authenticate
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope='playlist-modify-public playlist-modify-private playlist-read-private user-read-playback-state user-modify-playback-state app-remote-control',
                                               username=username))

# Get playlist tracks
playlist = sp.playlist(playlist_id)

# Get the playlist name
playlist_name = playlist['name']

# Sanitize the folder name
output_path = f"{current_dir}/playlists"
output_folder = f"{output_path}/{sanitize_filename(playlist_name)}"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# get tracks
tracks = playlist['tracks']['items']

# Get the current playback information
playback_info = sp.current_playback()

# Check if something is playing
if playback_info and playback_info['is_playing']:
    sp.pause_playback()
else:
    print("Playback is already paused or no active device found.")

# get current volume
if playback_info:
    volume_percent = playback_info['device']['volume_percent']
    print(f"original Spotify volume is {volume_percent}%")
else:
    print("No active device found")

# Get the current output device
current_device = subprocess.check_output(['SwitchAudioSource', '-c']).decode().strip()
print(f"original device is {current_device}")

original_volume = get_volume()
print(f"Original system volume is {original_volume}%")

# Set the output device to BlackHole
print(f"switching...")
os.system(f'SwitchAudioSource -s "{blackhole_id}"')
new_device = subprocess.check_output(['SwitchAudioSource', '-c']).decode().strip()
print(f"new device is {new_device}")

print(f"setting system volume to 100%")
set_volume(100)
print(f"setting Spotify volume to 100%")
set_volume(100)

devices = sp.devices()
device_id = devices['devices'][0]['id'] # Assuming the first device is the one you want
sp.volume(volume_percent=100, device_id=device_id)

for index, item in enumerate(tracks):
    track_no = index + 1
    track_uri = item['track']['uri']
    song_name = item['track']['name']
    artist_name = ", ".join([artist['name'] for artist in item['track']['artists']])
    filename = f"{output_folder}/{track_no:02} - {sanitize_filename(artist_name)} - {sanitize_filename(song_name)}.wav"

    song_duration = (item['track']['duration_ms']) / 1000
    sox_command = [
        "sox",
        "-t", "coreaudio", blackhole_id,
        "-b", "16", "-c", "2", "-r", "48000",
       
        filename,  # Output filename with the desired output folder and filename
         "trim", "0", str(song_duration)  # Start position and duration in seconds
    ]
    sp.start_playback(uris=[track_uri])
    time.sleep(1)  # Adjust the delay as needed
    subprocess.run(sox_command)
    


# Set the volume back
print(f"switching back...")
print(f"setting Spotify volume to 100%")
sp.volume(volume_percent)

# Set the output device to BlackHole
os.system('SwitchAudioSource -s ' + "'" + current_device + "'")
print(f"current device is {current_device}")
print(f"setting system volume back to {original_volume}%")
set_volume(original_volume)

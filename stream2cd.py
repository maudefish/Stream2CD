import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os #to interface with blackhole
import sys
import subprocess
import time
from flask import Flask, request, redirect
import json


current_dir = os.getcwd()

load_dotenv(dotenv_path='./config.env')


def print_intro():
    intro = """                                                                                         

 \033[38;5;57m ░██████╗████████╗██████╗░███████╗░█████╗░███╗░░░███╗██████╗░░█████╗░██████╗░
 \033[38;5;56m ██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔══██╗████╗░████║╚════██╗██╔══██╗██╔══██╗
 \033[38;5;55m ╚█████╗░░░░██║░░░██████╔╝█████╗░░███████║██╔████╔██║░░███╔═╝██║░░╚═╝██║░░██║
 \033[38;5;54m ░╚═══██╗░░░██║░░░██╔══██╗██╔══╝░░██╔══██║██║╚██╔╝██║██╔══╝░░██║░░██╗██║░░██║
 \033[38;5;53m ██████╔╝░░░██║░░░██║░░██║███████╗██║░░██║██║░╚═╝░██║███████╗╚█████╔╝██████╔╝
 \033[38;5;52m ╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚═╝░░░░░╚═╝╚══════╝░╚════╝░╚═════╝░\033[0m

                                        by \033[38;5;52mKevin Rodriguez\033[0m \033[38;5;23;4mgithub.com/maudefish\033[0m

    """
    print(intro)

print_intro()

# helper functions
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

# setup from config.env

blackhole_id = "BlackHole 2ch"
client_id = os.environ.get('SPOTIPY_CLIENT_ID')
client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
redirect_uri = 'http://localhost:8888/callback/'
# username = os.environ.get('SPOTIPY_USERNAME')
# playlist_id = os.environ.get('PLAYLIST_ID')

# if not playlist_id:
#     playlist_url = input("Please enter the full link of the playlist: ")
#     # Assuming the playlist URL is something like "https://open.spotify.com/playlist/1a2B3c4D5e6F7g8H9i"
#     # Extracting the playlist ID by splitting the URL by "/" and taking the last part
#     playlist_id = playlist_url.split("/")[-1].split("?")[0]
# Read the access token and playlist ID from the file
with open('auth_info.json', 'r') as f:
    auth_info = json.load(f)

access_token = auth_info['access_token']
playlist_id = auth_info['playlist_id']

sp = spotipy.Spotify(auth=access_token)


# say hi
user_info = sp.current_user()
display_name = user_info['display_name']
print(f'Display Name: {display_name}')
print(f"Playlist ID: {playlist_id}")

# Get playlist tracks
playlist = sp.playlist(playlist_id)

# Get the playlist name
playlist_name = playlist['name']
print(f'Playlist Name: {playlist_name}\n')

# Sanitize the folder name
output_path = f"{current_dir}/playlists"
output_folder = f"{output_path}/{sanitize_filename(playlist_name)}"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# get tracks
tracks = playlist['tracks']['items']
total_tracks = len(tracks)

track_range = input(f"Enter the range of tracks to record (e.g. 5-10) from total {total_tracks} tracks. press Enter to record all tracks: ")
start_index = 0
end_index = None

if track_range:
    try:
        start_index, end_index = map(int, track_range.split('-'))
        start_index -= 1 # converting to 0-based index
        if end_index > total_tracks:
            end_index = total_tracks # Ensure that the end index does not exceed the total number of tracks
        print(f"You selected tracks {start_index + 1} to {end_index}")
    except ValueError:
        print("Invalid range format. Recording all tracks.")


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
    error_message = "ERROR: Try pressing play on your Spotify app and running the code again."
    print(error_message)
    sys.exit(1)  

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

new_vol = 99
print(f"setting system volume to {new_vol}%")
set_volume(new_vol)
print(f"setting Spotify volume to 100%")

devices = sp.devices()
device_id = devices['devices'][0]['id'] # Assuming the first device is the one you want
sp.volume(volume_percent=100, device_id=device_id)

for index, item in enumerate(tracks[start_index:end_index]):
    track_no = index + 1
    track_uri = item['track']['uri']
    song_name = item['track']['name']
    artist_name = ", ".join([artist['name'] for artist in item['track']['artists']])
    filename = f"{output_folder}/{track_no:02} - {sanitize_filename(artist_name)} - {sanitize_filename(song_name)}.wav"
    print(f"Recording track: {filename}")
    song_duration = (item['track']['duration_ms']) / 1000

    # Check if the previous song is done playing
    while True:
        playback_info = sp.current_playback()
        if playback_info is None or not playback_info['is_playing']:
            break
        if playback_info['item']['id'] != track_uri: # Check if a new track has started playing
            break
        time.sleep(1) # Sleep for 1 second
    sox_command = [
        "sox",
        "-t", "coreaudio", blackhole_id,
        "-b", "16", "-c", "2", "-r", "48000",
        filename,  # Output filename with the desired output folder and filename
        "trim", "0", str(song_duration)  # Start position and duration in seconds
    ]

    # Start recording with Sox (non-blocking)
    sox_process = subprocess.Popen(sox_command)

    # Check if the previous song is done playing
    while True:
        playback_info = sp.current_playback()
        if playback_info is None or not playback_info['is_playing']:
            break
        if playback_info['item']['id'] != track_uri: # Check if a new track has started playing
            break
        time.sleep(1) # Sleep for 1 second

    # Start playback
    sp.start_playback(uris=[track_uri])

    # Wait for the Sox recording process to finish
    sox_process.wait()

    time.sleep(1) # Adjust the delay as needed
    

# Set the volume back
print(f"switching back...")
print(f"setting Spotify volume to 100%")
sp.volume(volume_percent)

print(f"setting system volume back to {original_volume}%")
set_volume(original_volume)

# Set the output device to original 
os.system('SwitchAudioSource -s ' + "'" + current_device + "'")
print(f"current device is {current_device}")


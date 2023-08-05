# Stream2CD

Stream2CD is a Python project that automates the process of saving music to local storage. This project is useful for creating personal offline backup copies of your favorite playlists. Please note that such backups may not be shared with others and may only be held for 30 days as per ToS. 


## Prerequisites

1. [Python 3.8](https://www.python.org/downloads/) or above
2. [pip](https://pip.pypa.io/en/stable/installation/)
3. [BlackHole](https://github.com/ExistentialAudio/BlackHole) (macOS only)
4. [SoX](http://sox.sourceforge.net/)

On macOS, you can install BlackHole and SoX using [Homebrew](https://brew.sh/):

```bash
brew install --cask blackhole-2ch
brew install sox
```
## Installation

To set up this project, follow these steps:

1. Clone the repository
```bash
git clone https://github.com/maudefish/Stream2CD.git
cd Stream2CD
```
2. Install python dependencies
```bash
pip install -r requirements.txt
```
3. Open the file named `empty.env` and fill out the environment variables:
```bash
SPOTIPY_CLIENT_ID=your-spotipy-client-id
SPOTIPY_CLIENT_SECRET=your-spotipy-client-secret
SPOTIPY_REDIRECT_URI=your-spotipy-redirect-uri
SPOTIPY_USERNAME=your-spotify-username
PLAYLIST_ID=your-playlist-id
```
Be sure to use your actual login credentials and playlist information.

4. Save the file as `config.env`

## Usage

After completing the steps above, you can run the program as
```bash
python stream2cd.py
```


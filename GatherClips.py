import requests
import datetime
import pandas as pd
import os
import re
import argparse
from yt_dlp import YoutubeDL
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

# Tweakable limits
CATEGORY_CLIP_LIMIT = 20
CHANNEL_CLIP_LIMIT = 10
DAYS_BACK = 30

# Authenticate with Twitch API
def get_oauth_token(client_id, client_secret):
    response = requests.post('https://id.twitch.tv/oauth2/token', params={
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    })
    return response.json()['access_token']

# Get game ID by game name
def get_game_id(game_name, headers):
    response = requests.get('https://api.twitch.tv/helix/games', headers=headers, params={'name': game_name})
    return response.json()['data'][0]['id']

# Get user ID by username
def get_user_id(username, headers):
    response = requests.get('https://api.twitch.tv/helix/users', headers=headers, params={'login': username})
    return response.json()['data'][0]['id']

# Get top clips for game category
def get_top_category_clips(game_id, headers, limit=CATEGORY_CLIP_LIMIT):
    ended_at = datetime.datetime.utcnow().isoformat("T") + "Z"
    started_at = (datetime.datetime.utcnow() - datetime.timedelta(days=DAYS_BACK)).isoformat("T") + "Z"

    params = {
        'game_id': game_id,
        'first': limit,
        'started_at': started_at,
        'ended_at': ended_at
    }

    response = requests.get('https://api.twitch.tv/helix/clips', headers=headers, params=params)
    return response.json()['data']

# Get top clips for each channel filtered by category
def get_channel_category_clips(user_id, game_id, headers, limit=CHANNEL_CLIP_LIMIT):
    ended_at = datetime.datetime.utcnow().isoformat("T") + "Z"
    started_at = (datetime.datetime.utcnow() - datetime.timedelta(days=DAYS_BACK)).isoformat("T") + "Z"

    params = {
        'broadcaster_id': user_id,
        'first': 300,
        'started_at': started_at,
        'ended_at': ended_at
    }

    response = requests.get('https://api.twitch.tv/helix/clips', headers=headers, params=params)
    clips = [clip for clip in response.json()['data'] if clip['game_id'] == game_id][:limit]
    return clips

# Load channel list from file
def load_channels(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Download the clip
def download_clip(clip, folder='clips'):
    if not os.path.exists(folder):
        os.makedirs(folder)

    def safe_filename(s):
        s = s.replace(' ', '_')
        s = re.sub(r'[^a-zA-Z0-9-_]', '', s)
        return s[:50]

    channel = safe_filename(clip['broadcaster_name'])
    title = safe_filename(clip['title'])

    ydl_opts = {
        'outtmpl': f'{folder}/{channel}-{title}.%(ext)s',
        'quiet': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            print(f"Downloading clip: {channel}-{title}")
            ydl.download([clip['url']])
            print(f"Downloaded successfully to {folder}")
        except Exception as e:
            print(f"Failed to download {clip['url']}: {e}")

# Threaded download
def threaded_download(clips, folder='clips', max_workers=5):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(download_clip, clip, folder) for clip in clips]
        for future in as_completed(futures):
            future.result()

def main(download=False):
    token = get_oauth_token(CLIENT_ID, CLIENT_SECRET)
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {token}'
    }

    game_name = 'SMITE 2'
    game_id = get_game_id(game_name, headers)

    channel_list = load_channels('channels.txt')
    top_category_clips = get_top_category_clips(game_id, headers, limit=20)

    with pd.ExcelWriter('matched_clips.xlsx', engine='xlsxwriter') as writer:
        top_df = pd.DataFrame(top_category_clips)
        top_df = top_df[['title', 'broadcaster_name', 'view_count', 'created_at', 'url']]
        top_df.to_excel(writer, sheet_name='Top Clips', index=False)

        for channel in channel_list:
            user_id = get_user_id(channel, headers)
            channel_clips = get_channel_category_clips(user_id, game_id, headers, limit=10)

            if channel_clips:
                df = pd.DataFrame(channel_clips)
                df = df[['title', 'broadcaster_name', 'view_count', 'created_at', 'url']]
                df.to_excel(writer, sheet_name=channel[:31], index=False)

        print("Output written to matched_clips.xlsx")

    if download:
        print("Downloading Clips...")
        threaded_download(top_category_clips, folder='clips/SMITE2_Category_Clips')

        for channel in channel_list:
            user_id = get_user_id(channel, headers)
            channel_clips = get_channel_category_clips(user_id, game_id, headers, limit=10)
            if channel_clips:
                threaded_download(channel_clips, folder=f"clips/{channel}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Fetch and optionally download Twitch clips.")
    parser.add_argument('--download', action='store_true', help='Download clips if set')

    args = parser.parse_args()

    main(download=args.download)
# Twitch SMITE 2 Clip Fetcher

## Overview
This script retrieves the top Twitch clips from the "SMITE 2" category over the last 30 days. It also fetches the top clips from user-defined channels, outputs them into an Excel file, and optionally downloads the clips as `.mp4` files.

## Requirements
- Python 3.x
- Twitch API credentials (`CLIENT_ID` and `CLIENT_SECRET` in `.env`)
- Dependencies:
```
pip install requests python-dotenv pandas xlsxwriter yt-dlp
```

## Usage
- Populate `channels.txt` with Twitch channel usernames (one per line).
- Run the script:
```bash
python GatherClips.py [--download]
```
`--download`: Optional flag to download clips.

## Output
- `matched_clips.xlsx`: Excel file containing fetched clip information.
- `clips/`: Directory containing downloaded clips (if `--download` is used).

## Register a Twitch App

To get a `CLIENT_ID` and `CLIENT_SECRET` for auth you'll need to register an application on the [Twitch Dev Console](https://dev.twitch.tv/console).
 - Register an App
 - Set a Name
 - Set redirect to `https://localhost`
 - Analytics tool
 - Confidential

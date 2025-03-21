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

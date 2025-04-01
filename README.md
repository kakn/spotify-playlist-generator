# spotify-playlist-generator
A Python-based tool that automates the creation of Spotify playlists marked as “unreleased,” with the goal of appearing in user-generated search results. By gathering YouTube playlist data for unreleased music, checking track availability on Spotify, and programmatically creating new playlists for any missing music, it aims to provide a free, automated way to boost artist visibility.

## How it works
- YouTube Scraping: Collects playlists and track details for “unreleased” music.
- Spotify Cross-Reference: Searches for these tracks on Spotify or existing “unreleased” playlists.
- Playlist Creation: If a track is absent, the tool creates a new playlist titled after the missing track, ensuring it appears in search results.

Currently, the project is being refactored from the “legacy” folder, which holds older, less-optimized code. Over time, this code will be streamlined into a cleaner, more efficient pipeline.

## Folder structure overview
- src/api_clients/spotify_api_client.py – Handles Spotify API interaction (authentication, data retrieval, and CSV merging).
- legacy/spotify_playlist_generator/ – Contains older scraping scripts for Spotify and YouTube (yt_playlist_scraper.py, yt_playlist_parser.py).

# Development Journal
### Unreleased Artist Data Collection (September 25 2024)
- Need to get list of artist names first, before trying search suggestions. Can get the top 10,000 or so artists and check to see if they appear in "unreleased" search suggestions.
- Could also do nested thrice, then cross-reference with top x artists on Spotify.
- Try multi-threading for nested loops
- Implement workaround for 403 error with too many requests. Maybe switch out the headers and stuff
- Use numbers too and potentially symbols.
- Keep matching infinitely maybe? Stop searching with current letter combination when results are less than 10? Depth-first search?
- Breadth-first search is also a good approach. Stop when results are less than 10
- Can sort artist popularity by how many times their name appears in search results.
### Spotify Top Rock Artist Data Collection (September 30 2024)
- Should make an abstract class for spotify_api_client and youtube_api_client so that they both rotate shit
- Figure out what genres my favorite artists are. I'm thinking "pov: indie", "shoegaze", "alternative rock"?
- Use all the genres that I think would be useful
- Collect thumnails or images too. This is important in the event the thumbnail does not work
- Use Youtube search API to filter out artists who do not have unreleased music
- Implement Proxy and User Agent rotation to get all search suggestions
### Continuation on Spotify Top Artist Data
- Get list of all genres on Spotify, collect top 1000 artists for each genre.
    - Or find a better way to collect top artist info
    - Maybe make a recursive implementation that starts with pop, collects all related genres, and so forth.
- Maybe the genre approach is too extensive. There are probably like 10,000 different genres. 
    - With 1 thousand artists in each genre??? 10 million artists to search for???
- Can't actually directly search for playlists by name. It looks at all metadata. I have made a request-heavy implementation to fix this
    - This does not bode well for when checking if a playlist exists by name later in the pipeline.
- Can check if song "is on streaming services" by seeing if the song in the YouTube playlist is posted by the official channel.
    - Furthermore, can validate this / nullify this if the "official song" is found later in the same or one of the other 2 playlists we look at on YouTube.
- Should use the full list of artists (_other_), as they likely have a higher concentration of unreleased music. Could maybe just scrape the internet for unreleased artists.
    - Should not have a limit when counting playlists
    - Get more API keys to rotate. Should be logging changing them
    - Should prioritize followers, not the genre of playlists.
### Analyzing artists that have unreleased music
- Sort new CSV by number of unreleased playlists, then followers
- Collect images that fit in Spotify playlist dimension
- Identify if scraped YouTube channel has "- Topic" in the name, this may imply the music is available on Spotify
- Create reliable RegEx scheme for cleaning YouTube videos. 
    - If the video has "Lyrics" in the name, might be best to use non-thumbnail as Spotify picture.
- Fuck, I may need a better Spotify playlist collection scheme. Name cannot be a part of a word, i.e. "Dio" has 11 playlists, but this could be "Celine Dion"
    - Use Unidecode
    - Perhaps also normalize "$", like in A$AP or $uicideBoy$
    - Also use lower case when trying to match, i.e. "unreleased alex g"
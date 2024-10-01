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
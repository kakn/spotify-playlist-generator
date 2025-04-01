# spotify
* Split by (feat. feat ft and ft.) when searching for songs
* Look for podcasts that contain all elements of the song title
* Tags in the description - increase visibility
* Look into what's being lost in the except statement (Unicode Error)
* * Seemingly nothing
* Strip whitespaces, features, quotation marks in names
* There's also the concern of not features but commas. 
* * Some artists have commas in there name, so splitting by comma won't always work
* Cross reference videoID's found in the JSON but not the CSV. These can have a closer look 
* Check for N/A - string containing N/A
* Might be best to have playlist name just be the video title
* * Perhaps if the artist name does not exist on Spotify (clearly something is wrong)
* if artist name does not exist, then strip () from the name and try again
* Look for "unknown" as well
* Look for (remixed by) in artist title
* feat might have to be thrown on the other side (song name)
* query should really have said "exclude features"
* Write a feature finder function - searches artist and track
* Gather all songs not included in songlist - most are probably crap so look at the popular ones
* Search tiktok songs next 
* * Search if it has playlist, if not, then check if the cleaned version has a playlist
* Cleaned version -> strip lyrics, official video, audio
* Strip leading or trailing hyphens too
* Should do OpenAI on potential_playlists, get rid of entries that aren't songs
* Check if spotify recognizes it as a song, then use openAi and see if spotify knows, if not, playlist time
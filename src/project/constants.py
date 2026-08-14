PROGRAMME_NAME = "Add to Playlist"
PROGRAMME_ID = "m00106lb"
BASE_PAGE_TITLE = f"{PROGRAMME_NAME} (BBC Radio 4)"

BBC_PROGRAMME_URL = "https://www.bbc.co.uk/programmes/"
SPOTIFY_TRACK_URL = "https://open.spotify.com/track/"
SPOTIFY_PLAYLIST_URL = "https://open.spotify.com/playlist/"

ARTIST_LEADERBOARD_AMOUNT = 25
PRESENTER_LEADERBOARD_AMOUNT = 10

# Spotify serves each album image at three sizes from the same 24-character id;
# only the prefix differs. Undocumented but long-stable, and storing the id
# rather than three URLs keeps the data a third of the size.
SPOTIFY_IMAGE_URL = "https://i.scdn.co/image/"
SPOTIFY_IMAGE_PREFIXES = {
    640: "ab67616d0000b273",
    300: "ab67616d00001e02",
    64: "ab67616d00004851",
}

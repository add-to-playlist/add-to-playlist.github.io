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

# Playlist of all tracks
ALL_PLAYLIST_ID = "2PgU4Fct9zICx1Hbt4X8N0"

# Playlists of each series (in order)
SERIES_PLAYLIST_IDS = (
    "4HLH5EHjBPOpXuLto27Cf2",  # 1
    "0757rUOarwlkD2olfe7sRo",  # 2
    "29PDzvsHMt25PHW4xHW5Js",  # 3
    "4mwdzqcSij07oa1NRnPAju",  # 4
    "5qyhiiEWSnEqRBQ6wpFWCY",  # 5
    "0dremLIKIqv5Nd8geXlwDI",  # 6
    "1fFOSM0O7ZHfkHq0H0TSIO",  # 7
    "0Ds5lazcAbTyJk4Znq4442",  # 8
    "0e7JreuqtEFYMcNTTClDVC",  # 9
    "3TEi3V4NPez2gxSQPSrEON",  # 10
    "5wqzfsRuWIWtMod5ro0MpV",  # 11
    "7b93UoWr6TY0LFfQIMYkMC",  # 12
    "4A4zUOpersExaZmgbBygs1",  # 13
    "0u91zsKlBcsnfeFkqcfSNG",  # 14
    "7EL2wFkXWFZblO8zu8Q2A8",  # 15
    "72M7ej4xKe0imadf9eFKjO",  # 16
    "0axZqEALB6cLIpssusL5wp",  # 17
    "4aahJnWt3af4j7Sf9tQwl0",  # 18
)

from .constants import (
    BBC_PROGRAMME_URL,
    SPOTIFY_ARTIST_URL,
    SPOTIFY_PLAYLIST_URL,
    SPOTIFY_TRACK_URL,
)

ARTISTS_PATH = "artists"
PRESENTERS_PATH = "presenters"
TRACKS_PATH = "tracks"


def bbc_programme_url(pid: str):
    return f"{BBC_PROGRAMME_URL}{pid}"


def spotify_artist_url(artist_id: str):
    return f"{SPOTIFY_ARTIST_URL}{artist_id}"


def spotify_track_url(track_id: str):
    return f"{SPOTIFY_TRACK_URL}{track_id}"


def spotify_playlist_url(playlist_id: str):
    return f"{SPOTIFY_PLAYLIST_URL}{playlist_id}"


def series_path(series_number: int):
    return f"series-{series_number}"


def episode_path(series_number: int, episode_number: int):
    return f"{series_path(series_number)}/episode-{episode_number}"


def get_page_url_path(series_number: int, episode_number: int | None = None):
    if episode_number is None:
        return series_path(series_number)

    return episode_path(series_number, episode_number)


def get_page_canonical_url(
    base_url: str, series_number: int, episode_number: int | None = None
):
    url_path = get_page_url_path(series_number, episode_number)
    return site_url(base_url, url_path)


def site_url(base_url: str, url_path: str = ""):
    """Absolute, trailing-slashed URL for a page.

    The single source of every page URL - used for canonical tags, JSON-LD
    `url` and `@id`, breadcrumbs and sitemap entries, so they cannot disagree.
    """
    if not url_path:
        return f"{base_url.rstrip('/')}/"

    return f"{base_url.rstrip('/')}/{url_path.strip('/')}/"

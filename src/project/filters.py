from datetime import datetime

from project.constants import SERIES_PLAYLIST_IDS
from project.models import Series, Track
from project.urls import spotify_playlist_url, spotify_track_url


class MediaLinkException(Exception): ...


def date_format(value: str):
    dt = datetime.fromisoformat(value)
    return f"{dt.day} {dt.strftime('%B %Y')}"


def datetime_format(value: str) -> str:
    dt = datetime.fromisoformat(value)
    time_part = dt.strftime("%I:%M%p").lstrip("0").lower()
    return f"{dt.day} {dt.strftime('%B %Y')}, {time_part}"


def month_year_format(value: str):
    return datetime.fromisoformat(value).strftime("%B %Y")


def join_names(names: list[str], conjunction: str = "and"):
    if not names:
        return ""

    if len(names) <= 2:
        return f" {conjunction} ".join(names)

    return f"{', '.join(names[:-1])}, {conjunction} {names[-1]}"


def duration_format(total_seconds: int):
    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60

    if hours == 0:
        return f"{minutes} minutes"

    return f"{hours} hours {minutes} minutes"


def get_playlist_id(series: Series):
    return SERIES_PLAYLIST_IDS[series.number - 1]


def media_link(track: Track):
    if track.spotify_id is not None:
        return spotify_track_url(track.spotify_id)
    elif track.youtube is not None:
        return track.youtube
    else:
        raise MediaLinkException("Unknown media link")


def table_class_name(number: int):
    return "td-even" if (number % 2) == 0 else "td-odd"


filters = {
    "date_format": date_format,
    "datetime_format": datetime_format,
    "duration_format": duration_format,
    "get_playlist_id": get_playlist_id,
    "join_names": join_names,
    "media_link": media_link,
    "month_year_format": month_year_format,
    "spotify_playlist_url": spotify_playlist_url,
    "table_class_name": table_class_name,
}

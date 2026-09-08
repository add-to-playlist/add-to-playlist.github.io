from itertools import chain

from project.urls import (
    bbc_programme_url,
    spotify_artist_url,
    spotify_playlist_url,
    spotify_track_url,
)

from .constants import (
    ALL_PLAYLIST_ID,
    PROGRAMME_ID,
    PROGRAMME_NAME,
    SERIES_PLAYLIST_IDS,
)
from .models import Episode, Series, SeriesCollection, Track
from .utils import seconds_to_iso8601


def document(nodes: list[dict]):
    return {"@context": "https://schema.org", "@graph": nodes}


def node_id(url: str, id: str):
    return f"{url.rstrip('/')}/#{id}"


def programme_node(home_url: str):
    return {
        "@type": "RadioSeries",
        "@id": node_id(home_url, "programme"),
        "name": PROGRAMME_NAME,
        "url": home_url,
        "sameAs": bbc_programme_url(PROGRAMME_ID),
    }


def series_node(home_url: str, canonical_url: str, series: Series):
    node_data = {
        "@type": "RadioSeason",
        "@id": node_id(canonical_url, "season"),
        "name": f"{PROGRAMME_NAME}, Series {series.number}",
        "seasonNumber": series.number,
        "numberOfEpisodes": len(series.episodes),
        "url": canonical_url,
        "partOfSeries": {"@id": node_id(home_url, "programme")},
    }

    if series.id is not None:
        node_data["identifier"] = series.id
        node_data["sameAs"] = bbc_programme_url(series.id)

    return node_data


def episode_node(
    home_url: str,
    canonical_url: str,
    series_url: str,
    episode: Episode,
):
    return {
        "@type": "RadioEpisode",
        "@id": node_id(canonical_url, "episode"),
        "name": episode.name,
        "episodeNumber": episode.number,
        "url": canonical_url,
        "identifier": episode.id,
        "datePublished": episode.released,
        "duration": seconds_to_iso8601(episode.duration_seconds),
        "sameAs": bbc_programme_url(episode.id),
        "partOfSeries": {"@id": node_id(home_url, "programme")},
        "partOfSeason": {"@id": node_id(series_url, "season")},
        "publication": [
            {
                "@type": "BroadcastEvent",
                "startDate": episode.broadcast,
                "publishedOn": {"@type": "BroadcastService", "name": "BBC Radio 4"},
            },
            {
                "@type": "OnDemandEvent",
                "startDate": episode.released,
                "publishedOn": {"@type": "BroadcastService", "name": "BBC Sounds"},
            },
        ],
    }


def playlist_node(
    canonical_url: str,
    name: str,
    part_of: str,
    tracks: list[Track],
    same_as: str | None = None,
):
    node_data = {
        "@type": "MusicPlaylist",
        "@id": node_id(canonical_url, "playlist"),
        "name": name,
        "numTracks": len(tracks),
        "url": canonical_url,
        "isPartOf": {"@id": node_id(canonical_url, part_of)},
        "track": {
            "@type": "ItemList",
            "itemListOrder": "ItemListOrderAscending",
            "itemListElement": [
                track_list_item_node(track, position=x)
                for x, track in enumerate(tracks, start=1)
            ],
        },
    }

    if same_as is not None:
        node_data["sameAs"] = same_as

    return node_data


def all_tracks_playlist_node(
    home_url: str,
    canonical_url: str,
    all_series: SeriesCollection,
):
    return {
        "@type": "MusicPlaylist",
        "@id": node_id(canonical_url, "playlist"),
        "name": f"{PROGRAMME_NAME} - every track",
        "numTracks": all_series.track_count,
        "url": canonical_url,
        "isPartOf": {"@id": node_id(home_url, "programme")},
        "sameAs": spotify_playlist_url(ALL_PLAYLIST_ID),
    }


def series_playlist_node(canonical_url: str, series: Series):
    return playlist_node(
        canonical_url=canonical_url,
        name=f"{PROGRAMME_NAME}, Series {series.number} - playlist",
        part_of="season",
        tracks=list(chain.from_iterable(series)),
        same_as=spotify_playlist_url(SERIES_PLAYLIST_IDS[series.number - 1]),
    )


def episode_playlist_node(canonical_url: str, episode: Episode):
    return playlist_node(
        canonical_url=canonical_url,
        name=(
            f"{PROGRAMME_NAME}, Series {episode.series} "
            f"Episode {episode.number} - playlist"
        ),
        part_of="episode",
        tracks=list(episode),
    )


def track_list_item_node(track: Track, position: int):
    node_data = {
        "@type": "ListItem",
        "position": position,
        "item": {
            "@type": "MusicRecording",
            "name": track.name,
        },
    }

    if track.connection is not None:
        node_data["description"] = track.connection

    if track.artists is not None:
        node_data["item"]["byArtist"] = [
            music_group_node(item) for item in track.artists
        ]

    if track.isrc_code is not None:
        node_data["item"]["isrcCode"] = track.isrc_code

    if track.duration_ms is not None:
        node_data["item"]["duration"] = seconds_to_iso8601(
            round(track.duration_ms / 1000)
        )

    if track.spotify_id is not None:
        node_data["item"]["sameAs"] = spotify_track_url(track.spotify_id)

    return node_data


def music_group_node(artist: str):
    return {"@type": "MusicGroup", "name": artist}


def artist_leaderboard_node(
    canonical_url: str,
    leaderboard: list[dict],
    first_broadcast_date: str,
):
    return {
        "@type": "ItemList",
        "@id": node_id(canonical_url, "artist-leaderboard"),
        "name": f"{PROGRAMME_NAME} - most-chosen artists",
        "description": (
            "Artists ranked by how many of their tracks have been chosen on "
            f"{PROGRAMME_NAME}. Artists tied on the same total share a joint "
            "position."
        ),
        "url": canonical_url,
        "numberOfItems": len(leaderboard),
        "itemListOrder": "ItemListOrderDescending",
        "itemListElement": [
            artist_list_item_node(
                artist=artist,
                position=x,
                first_broadcast_date=first_broadcast_date,
            )
            for x, artist in enumerate(leaderboard, start=1)
        ],
    }


def artist_list_item_node(artist: dict, position: int, first_broadcast_date: str):
    count = artist["count"]
    rank = artist["rank"]
    times = "time" if count == 1 else "times"

    return {
        "@type": "ListItem",
        "position": position,
        "description": f"{rank} - chosen {count} {times} since {first_broadcast_date}",
        "item": {
            **music_group_node(", ".join(artist["names"])),
            "sameAs": spotify_artist_url(artist["id"]),
        },
    }


def breadcrumb_node(crumbs: list[tuple[str, str]]):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            breadcrumb_item_node(position=x, name=name, url=url)
            for x, (name, url) in enumerate(crumbs, start=1)
        ],
    }


def breadcrumb_item_node(position: int, name: str, url: str):
    return {
        "@type": "ListItem",
        "position": position,
        "name": name,
        "item": url,
    }

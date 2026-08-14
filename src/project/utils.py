import os

from collections import defaultdict

from project.models import PresenterLeaderboardRow, SeriesCollection

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
)


def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return str(n) + suffix


def get_page_build_path(
    base_dir: str, *, series_number: int, episode_number: int | None = None
):
    paths = [base_dir, f"series-{series_number}"]

    if episode_number is not None:
        paths.append(f"episode-{episode_number}")

    paths.append("index.html")

    return os.path.join(*paths)


def seconds_to_iso8601(total_seconds: int) -> str:
    if total_seconds < 0:
        raise ValueError("value must be non-negative")

    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    result = "PT"

    if hours:
        result += f"{hours}H"

    if minutes:
        result += f"{minutes}M"

    if seconds or not (hours or minutes):
        result += f"{seconds}S"

    return result


def get_rank_labels(leaderboard: list):
    all_totals = []
    unique_totals = []
    ranks = {}
    current_rank = 1

    for item in leaderboard:
        total = item["count"]
        all_totals.append(total)

        if total not in unique_totals:
            unique_totals.append(total)

    for total in unique_totals:
        occurrences = all_totals.count(total)
        is_shared = occurrences > 1
        label = ordinal(current_rank)

        if is_shared:
            label = "Joint " + label

        ranks[total] = label
        current_rank += occurrences

    return ranks


def get_artist_leaderboard(
    all_series: SeriesCollection,
    amount: int,
):
    all_artists = {}
    leaderboard = []

    for series in all_series:
        for episode in series:
            for track in episode:
                if track.spotify is not None and track.spotify.artists:
                    for artist in track.spotify.artists:
                        if artist.id not in all_artists:
                            all_artists[artist.id] = {
                                "count": 0,
                                "names": [],
                                "tracks": [],
                            }

                        entry = all_artists[artist.id]

                        entry["count"] += 1

                        if artist.name not in entry["names"]:
                            entry["names"].append(artist.name)

                        entry["tracks"].append(
                            {
                                "series": series.number,
                                "episode": episode.number,
                                "number": track.number,
                                "name": track.name,
                                "episode_url": episode.url,
                            }
                        )

    for item in all_artists.values():
        leaderboard.append(
            {
                "names": item["names"],
                "count": item["count"],
                "tracks": item["tracks"],
            }
        )

    leaderboard.sort(key=lambda x: x["count"], reverse=True)

    leaderboard = leaderboard[:amount]
    rank_labels = get_rank_labels(leaderboard)

    for item in leaderboard:
        item["rank"] = rank_labels[item["count"]]

    return leaderboard


def get_presenter_leaderboard(
    all_series: SeriesCollection,
    amount: int,
):
    leaderboard = []
    d = defaultdict(list)

    for episode in all_series.episodes:
        for track in episode:
            d[track.chosen_by].append(
                PresenterLeaderboardRow(
                    date=episode.broadcast,
                    series=episode.series,
                    episode=episode.number,
                    track=track,
                )
            )

    sorted_d = dict(sorted(d.items(), key=lambda item: len(item[1]), reverse=True))

    for x, (presenter, tracks) in enumerate(sorted_d.items()):
        leaderboard.append(
            {
                "name": presenter,
                "count": len(tracks),
                "picks": tracks,
            }
        )

        if (x + 1) >= amount:
            break

    rank_labels = get_rank_labels(leaderboard)

    for item in leaderboard:
        item["rank"] = rank_labels[item["count"]]

    return leaderboard

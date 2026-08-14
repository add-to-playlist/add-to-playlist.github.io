from collections import defaultdict

from .models import SeriesCollection


def track_label(track: dict):
    """Chart-friendly label, e.g. "S01E01 - Old Town Road"."""
    return f"S{track['series']:02}E{track['episode']:02} - {track['name']}"


def build_bar_chart(artist_leaderboard: list):
    return {
        "bar_chart_data": [item["count"] for item in artist_leaderboard],
        "bar_chart_labels": [", ".join(item["names"]) for item in artist_leaderboard],
        "bar_chart_tracks": [
            [track_label(track) for track in item["tracks"]]
            for item in artist_leaderboard
        ],
    }


def build_heatmap(
    all_series: SeriesCollection,
    artist_leaderboard: list,
    artist_labels: list,
):
    series_numbers = [series.number for series in all_series]
    data = []

    for label, item in zip(artist_labels, artist_leaderboard):
        by_series = defaultdict(list)

        for track in item["tracks"]:
            by_series[track["series"]].append(track_label(track))

        for number in series_numbers:
            tracks = by_series[number]
            data.append(
                {
                    "x": str(number),
                    "y": label,
                    "v": len(tracks),
                    "tracks": tracks,
                }
            )

    return {
        "heatmap_artists": artist_labels,
        "heatmap_data": data,
        "heatmap_series": [str(number) for number in series_numbers],
    }

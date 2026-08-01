import hashlib
import json
import os

import minify_html

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from project.filters import filters
from project.models import SeriesCollection
from project.utils import (
    ALL_PLAYLIST_ID,
    get_artist_leaderboard,
    get_presenter_leaderboard,
)

EPISODE_DATA_PATH = os.environ.get("EPISODE_DATA_PATH", "data.json")
OUTPUT_HTML_PATH = os.environ.get("OUTPUT_HTML_PATH", "../assets/index.html")
SITE_BASE_URL = os.environ.get("SITE_BASE_URL", "https://add-to-playlist.github.io/")
GOOGLE_SITE_VERIFICATION_ID = os.environ.get("GOOGLE_SITE_VERIFICATION_ID")


def canonical_url():
    return SITE_BASE_URL.rstrip("/") + "/"


def latest_broadcast_date(all_series: SeriesCollection):
    return max(episode.broadcast for episode in all_series.episodes)[:10]


def render_sibling_file(
    env: Environment,
    template_name: str,
    file_name: str,
    **context,
):
    """Render a template to a file alongside the output HTML."""
    output = env.get_template(template_name).render(**context)

    path = os.path.join(os.path.dirname(OUTPUT_HTML_PATH), file_name)

    with open(path, mode="w", encoding="utf8") as f:
        f.write(output)


def load_series_data():
    with open(
        EPISODE_DATA_PATH,
        mode="r",
        encoding="utf8",
    ) as f:
        return SeriesCollection(episodes=json.load(f))


def main():
    env = Environment(
        loader=FileSystemLoader("templates"),
        undefined=StrictUndefined,
        lstrip_blocks=True,
        trim_blocks=True,
    )

    env.filters.update(filters)
    env.globals["TABLE_CLASSES"] = "striped"

    template = env.get_template("index.j2")

    all_series = load_series_data()

    artist_leaderboard_amt = 25
    artist_leaderboard = get_artist_leaderboard(
        all_series=all_series,
        amount=artist_leaderboard_amt,
    )

    presenter_leaderboard_amt = 10
    presenter_leaderboard = get_presenter_leaderboard(
        all_series=all_series,
        amount=presenter_leaderboard_amt,
    )

    bar_chart_labels = [", ".join(item["names"]) for item in artist_leaderboard]
    bar_chart_data = [item["count"] for item in artist_leaderboard]
    bar_chart_tracks = [
        [f"S{t['series']:02}E{t['episode']:02} - {t['name']}" for t in item["tracks"]]
        for item in artist_leaderboard
    ]

    series_numbers = [series.number for series in all_series]
    heatmap_series = [str(n) for n in series_numbers]
    heatmap_artists = bar_chart_labels
    heatmap_data = []
    for label, item in zip(bar_chart_labels, artist_leaderboard):
        by_series = {}
        for track in item["tracks"]:
            by_series.setdefault(track["series"], []).append(
                f"S{track['series']:02}E{track['episode']:02} - {track['name']}"
            )
        for n in series_numbers:
            tracks = by_series.get(n, [])
            heatmap_data.append(
                {"x": str(n), "y": label, "v": len(tracks), "tracks": tracks}
            )

    with open("../assets/styles.css", "rb") as f:
        styles_hash = hashlib.sha256(f.read()).hexdigest()[:12]

    output = template.render(
        all_series=all_series,
        all_series_playlist=ALL_PLAYLIST_ID,
        canonical_url=canonical_url(),
        og_image_url=canonical_url() + "images/icon.png",
        artist_leaderboard=artist_leaderboard,
        artist_leaderboard_amt=artist_leaderboard_amt,
        bar_chart_data=bar_chart_data,
        bar_chart_labels=bar_chart_labels,
        bar_chart_tracks=bar_chart_tracks,
        heatmap_series=heatmap_series,
        heatmap_artists=heatmap_artists,
        heatmap_data=heatmap_data,
        styles_hash=styles_hash,
        max_visible_artists=3,
        max_visible_picks=5,
        presenter_leaderboard=presenter_leaderboard,
        presenter_leaderboard_amt=presenter_leaderboard_amt,
    )

    minified = minify_html.minify(code=output, minify_js=True)

    with open(OUTPUT_HTML_PATH, mode="w", encoding="utf8") as f:
        f.write(minified)

    render_sibling_file(
        env=env,
        template_name="sitemap.j2",
        file_name="sitemap.xml",
        canonical_url=canonical_url(),
        lastmod=latest_broadcast_date(all_series),
    )

    render_sibling_file(
        env=env,
        template_name="robots.j2",
        file_name="robots.txt",
        sitemap_url=canonical_url() + "sitemap.xml",
    )

    if GOOGLE_SITE_VERIFICATION_ID is not None:
        file_name = f"google{GOOGLE_SITE_VERIFICATION_ID}.html"
        render_sibling_file(
            env=env,
            template_name="google_verification.j2",
            file_name=file_name,
            verification_file_name=file_name,
        )


if __name__ == "__main__":
    main()

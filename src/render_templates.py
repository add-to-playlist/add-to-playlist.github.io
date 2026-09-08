import json
import os
import shutil

from typing import NamedTuple

import minify_html

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from project.assets import make_asset_url
from project.charts import build_bar_chart, build_heatmap
from project.constants import (
    ALL_PLAYLIST_ID,
    ARTIST_LEADERBOARD_AMOUNT,
    BASE_PAGE_TITLE,
    PRESENTER_LEADERBOARD_AMOUNT,
    PROGRAMME_ID,
    PROGRAMME_NAME,
)
from project.filters import date_format, filters, join_names, month_year_format
from project.models import Episode, Series, SeriesCollection
from project.schema import (
    all_tracks_playlist_node,
    artist_leaderboard_node,
    breadcrumb_node,
    document,
    episode_node,
    episode_playlist_node,
    programme_node,
    series_node,
    series_playlist_node,
)
from project.urls import (
    ARTISTS_PATH,
    PRESENTERS_PATH,
    TRACKS_PATH,
    bbc_programme_url,
    episode_path,
    get_page_canonical_url,
    get_page_url_path,
    series_path,
    site_url,
)
from project.utils import (
    get_artist_leaderboard,
    get_presenter_leaderboard,
)

SERIES_DATA_PATH = os.environ.get("SERIES_DATA_PATH", "data/series.json")
EPISODE_DATA_PATH = os.environ.get("EPISODE_DATA_PATH", "data/episodes.json")
ASSETS_DIR = os.environ.get("ASSETS_DIR", "assets")
BUILD_DIR = os.environ.get("BUILD_DIR", "../build")
SITE_BASE_URL = os.environ.get(
    "SITE_BASE_URL",
    "https://add-to-playlist.github.io",
)
GOOGLE_SITE_VERIFICATION_ID = os.environ.get("GOOGLE_SITE_VERIFICATION_ID")


class Page(NamedTuple):
    loc: str
    lastmod: str


def get_canonical_url():
    return SITE_BASE_URL.rstrip("/") + "/"


def broadcast_date(value: str):
    """Date portion of an ISO timestamp, for sitemap lastmod."""
    return value[:10]


def latest_broadcast_date(all_series: SeriesCollection):
    return broadcast_date(max(episode.broadcast for episode in all_series.episodes))


def render_sibling_file(
    env: Environment,
    template_name: str,
    file_name: str,
    **context,
):
    """Render a template to a file alongside the output HTML."""
    output = env.get_template(template_name).render(**context)

    path = os.path.join(BUILD_DIR, file_name)

    with open(path, mode="w", encoding="utf8") as f:
        f.write(output)


def load_series_data():
    with open(
        SERIES_DATA_PATH,
        mode="r",
        encoding="utf8",
    ) as f:
        series_data = json.load(f)

    with open(
        EPISODE_DATA_PATH,
        mode="r",
        encoding="utf8",
    ) as f:
        episode_data = json.load(f)

    return SeriesCollection(series=series_data, episodes=episode_data)


def build_environment():
    env = Environment(
        loader=FileSystemLoader("templates"),
        undefined=StrictUndefined,
    )

    env.filters.update(filters)
    env.globals["asset"] = make_asset_url(ASSETS_DIR)
    env.globals["bbc_programme_url"] = bbc_programme_url
    env.globals["episode_path"] = episode_path
    env.globals["series_path"] = series_path
    env.globals["ARTISTS_PATH"] = ARTISTS_PATH
    env.globals["BASE_PAGE_TITLE"] = BASE_PAGE_TITLE
    env.globals["PRESENTERS_PATH"] = PRESENTERS_PATH
    env.globals["PROGRAMME_ID"] = PROGRAMME_ID
    env.globals["PROGRAMME_NAME"] = PROGRAMME_NAME
    env.globals["TABLE_CLASSES"] = "striped"
    env.globals["TRACKS_PATH"] = TRACKS_PATH

    return env


def prepare_build_dir():
    shutil.rmtree(path=BUILD_DIR, ignore_errors=True)
    shutil.copytree(src=ASSETS_DIR, dst=BUILD_DIR, dirs_exist_ok=True)


def render_home_page(env: Environment, all_series: SeriesCollection):
    return render_page(
        env=env,
        template_name="index.j2",
        url_path="",  # site root; the sitemap loc comes from canonical_url
        json_ld_nodes=[programme_node(home_url=get_canonical_url())],
        page_title=f"{BASE_PAGE_TITLE} - Complete Song and Track List",
        page_description=f"Every song and track from BBC Radio 4's {PROGRAMME_NAME}. Browse all {len(all_series)} series episode by episode, with links to Spotify and YouTube where available.",
        canonical_url=get_canonical_url(),
        lastmod=latest_broadcast_date(all_series),
        og_image_url=get_canonical_url() + "images/icon.png",
        all_series=all_series,
        all_series_playlist=ALL_PLAYLIST_ID,
        artist_leaderboard_amt=ARTIST_LEADERBOARD_AMOUNT,
    )


def render_tracks_page(env: Environment, all_series: SeriesCollection):
    return render_page(
        env=env,
        template_name="tracks.j2",
        url_path=TRACKS_PATH,
        json_ld_nodes=[
            breadcrumb_node(
                crumbs=[
                    ("Home", get_canonical_url()),
                    ("Every track", site_url(SITE_BASE_URL, TRACKS_PATH)),
                ],
            ),
            programme_node(home_url=get_canonical_url()),
            all_tracks_playlist_node(
                home_url=get_canonical_url(),
                canonical_url=f"{get_canonical_url()}{TRACKS_PATH}/",
                all_series=all_series,
            ),
        ],
        page_title=f"{BASE_PAGE_TITLE} - Every Track from Every Episode",
        page_description=f"The complete track list for {PROGRAMME_NAME}: all {all_series.track_count} tracks across {all_series.episode_count} episodes, with the connection between each one and who chose it.",
        canonical_url=f"{get_canonical_url()}{TRACKS_PATH}/",
        lastmod=latest_broadcast_date(all_series),
        og_image_url=get_canonical_url() + "images/icon.png",
        all_series=all_series,
        all_series_playlist=ALL_PLAYLIST_ID,
        max_visible_artists=3,
    )


def render_artists_page(env: Environment, all_series: SeriesCollection):
    artist_leaderboard = get_artist_leaderboard(
        all_series=all_series,
        amount=ARTIST_LEADERBOARD_AMOUNT,
    )
    bar_chart = build_bar_chart(artist_leaderboard=artist_leaderboard)
    heatmap = build_heatmap(
        all_series=all_series,
        artist_leaderboard=artist_leaderboard,
        artist_labels=bar_chart["bar_chart_labels"],
    )

    return render_page(
        env=env,
        template_name="artists.j2",
        url_path=ARTISTS_PATH,
        json_ld_nodes=[
            breadcrumb_node(
                crumbs=[
                    ("Home", get_canonical_url()),
                    ("Artists", site_url(SITE_BASE_URL, ARTISTS_PATH)),
                ],
            ),
            programme_node(home_url=get_canonical_url()),
            artist_leaderboard_node(
                canonical_url=f"{get_canonical_url()}{ARTISTS_PATH}/",
                leaderboard=artist_leaderboard,
                first_broadcast_date=date_format(all_series.first_broadcast),
            ),
        ],
        page_title=f"{BASE_PAGE_TITLE} - Most-Chosen Artists",
        page_description=f"The {ARTIST_LEADERBOARD_AMOUNT} artists chosen most often on {PROGRAMME_NAME}, as a table and as charts showing how their picks spread across the series.",
        canonical_url=f"{get_canonical_url()}{ARTISTS_PATH}/",
        lastmod=latest_broadcast_date(all_series),
        og_image_url=get_canonical_url() + "images/icon.png",
        all_series=all_series,
        artist_leaderboard=artist_leaderboard,
        artist_leaderboard_amt=ARTIST_LEADERBOARD_AMOUNT,
        max_visible_artists=3,
        **bar_chart,
        **heatmap,
    )


def render_presenters_page(env: Environment, all_series: SeriesCollection):
    presenter_leaderboard = get_presenter_leaderboard(
        all_series=all_series,
        amount=PRESENTER_LEADERBOARD_AMOUNT,
    )

    return render_page(
        env=env,
        template_name="presenters.j2",
        url_path=PRESENTERS_PATH,
        json_ld_nodes=[
            breadcrumb_node(
                crumbs=[
                    ("Home", get_canonical_url()),
                    ("Presenters", site_url(SITE_BASE_URL, PRESENTERS_PATH)),
                ],
            ),
            programme_node(home_url=get_canonical_url()),
        ],
        page_title=f"{BASE_PAGE_TITLE} - Presenters and Guests",
        page_description=f"Who picks the most tracks on {PROGRAMME_NAME}: the top {PRESENTER_LEADERBOARD_AMOUNT} presenters and guests, with every track each of them chose.",
        canonical_url=f"{get_canonical_url()}{PRESENTERS_PATH}/",
        lastmod=latest_broadcast_date(all_series),
        og_image_url=get_canonical_url() + "images/icon.png",
        all_series=all_series,
        presenter_leaderboard=presenter_leaderboard,
        presenter_leaderboard_amt=PRESENTER_LEADERBOARD_AMOUNT,
        max_visible_picks=5,
    )


def render_series_pages(env: Environment, all_series: SeriesCollection):
    pages: list[Page] = []

    for series in all_series:
        pages.append(_render_series_page(env, series))

    return pages


def series_page_description(series: Series):
    return (
        f"Series {series.number} of BBC Radio 4's {PROGRAMME_NAME}: "
        f"{len(series)} episodes and {series.track_count} tracks chosen by "
        f"{join_names(series.regular_presenters + ['their guests'])}, "
        f"{month_year_format(series.first_broadcast)} to "
        f"{month_year_format(series.last_broadcast)}."
    )


def _render_series_page(env: Environment, series: Series):
    canonical_url = get_page_canonical_url(
        base_url=SITE_BASE_URL, series_number=series.number
    )
    json_ld_nodes = [
        breadcrumb_node(
            crumbs=[
                ("Home", get_canonical_url()),
                (f"Series {series.number}", canonical_url),
            ],
        ),
        programme_node(home_url=get_canonical_url()),
        series_node(
            home_url=get_canonical_url(),
            canonical_url=canonical_url,
            series=series,
        ),
        series_playlist_node(canonical_url=canonical_url, series=series),
    ]

    return render_page(
        env=env,
        template_name="overview/series/index.j2",
        url_path=get_page_url_path(series_number=series.number),
        json_ld_nodes=json_ld_nodes,
        page_title=f"{BASE_PAGE_TITLE} - Series {series.number}",
        page_description=series_page_description(series),
        canonical_url=canonical_url,
        lastmod=broadcast_date(series.last_broadcast),
        og_image_url=get_canonical_url() + "images/icon.png",
        series=series,
    )


def render_episode_pages(env: Environment, all_series: SeriesCollection):
    all_episodes = all_series.episodes
    pages: list[Page] = []

    for i, episode in enumerate(all_episodes):
        prev_episode = all_episodes[i - 1] if i > 0 else None
        next_episode = all_episodes[i + 1] if i + 1 < len(all_episodes) else None

        pages.append(
            _render_episode_page(
                env=env,
                episode=episode,
                prev_episode=prev_episode,
                next_episode=next_episode,
            )
        )

    return pages


def episode_page_description(episode: Episode):
    return (
        f"Every track from {PROGRAMME_NAME} {episode.code}, first broadcast "
        f"{date_format(episode.broadcast)}: {episode.track_count} tracks chosen by "
        f"{join_names(episode.pickers)}, with the connection between each one."
    )


def _render_episode_page(
    env: Environment,
    episode: Episode,
    prev_episode: Episode | None,
    next_episode: Episode | None,
):
    canonical_url = get_page_canonical_url(
        base_url=SITE_BASE_URL,
        series_number=episode.series,
        episode_number=episode.number,
    )
    series_url = get_page_canonical_url(
        base_url=SITE_BASE_URL, series_number=episode.series
    )
    json_ld_nodes = [
        breadcrumb_node(
            crumbs=[
                ("Home", get_canonical_url()),
                (f"Series {episode.series}", series_url),
                (f"Episode {episode.number}", canonical_url),
            ],
        ),
        programme_node(home_url=get_canonical_url()),
        episode_node(
            home_url=get_canonical_url(),
            canonical_url=canonical_url,
            series_url=series_url,
            episode=episode,
        ),
        episode_playlist_node(canonical_url=canonical_url, episode=episode),
    ]

    return render_page(
        env=env,
        template_name="overview/episode/index.j2",
        url_path=get_page_url_path(
            series_number=episode.series, episode_number=episode.number
        ),
        json_ld_nodes=json_ld_nodes,
        episode=episode,
        prev_episode=prev_episode,
        next_episode=next_episode,
        page_title=f"{BASE_PAGE_TITLE} - {episode.code} - {episode.name}",
        page_description=episode_page_description(episode),
        canonical_url=canonical_url,
        lastmod=broadcast_date(episode.broadcast),
        og_image_url=get_canonical_url() + "images/icon.png",
    )


def render_page(
    env: Environment,
    template_name: str,
    url_path: str,
    canonical_url: str,
    lastmod: str,
    json_ld_nodes=None,
    skip_minify=False,
    **context,
):
    template = env.get_template(template_name)
    output_dir = os.path.join(BUILD_DIR, url_path)
    output = template.render(
        canonical_url=canonical_url,
        json_ld=document(json_ld_nodes) if json_ld_nodes else None,
        **context,
    )

    if not skip_minify:
        output = minify_html.minify(
            code=output,
            minify_js=True,
            keep_html_and_head_opening_tags=True,
            keep_closing_tags=True,
        )

    os.makedirs(name=output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "index.html"), mode="w", encoding="utf8") as f:
        f.write(output)

    return Page(loc=canonical_url, lastmod=lastmod)


def main():
    env = build_environment()
    all_series = load_series_data()

    prepare_build_dir()

    pages = [
        render_home_page(env, all_series),
        render_tracks_page(env, all_series),
        render_artists_page(env, all_series),
        render_presenters_page(env, all_series),
        *render_series_pages(env, all_series),
        *render_episode_pages(env, all_series),
    ]

    render_sibling_file(
        env=env,
        template_name="sitemap.j2",
        file_name="sitemap.xml",
        pages=pages,
    )

    render_sibling_file(
        env=env,
        template_name="robots.j2",
        file_name="robots.txt",
        sitemap_url=get_canonical_url() + "sitemap.xml",
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

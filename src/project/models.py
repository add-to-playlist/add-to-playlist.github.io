import dataclasses

from collections import defaultdict
from typing import Any, Literal

from .constants import SPOTIFY_IMAGE_PREFIXES, SPOTIFY_IMAGE_URL


class SeriesCollection:
    def __init__(self, series: list[str | None], episodes: list[dict[str, Any]]):
        self.episodes: list[Episode] = []
        self.series: list[Series] = []
        self._parse(series, episodes)

    def __getitem__(self, index: int):
        return self.series[index]

    def __iter__(self):
        return iter(self.series)

    def __len__(self):
        return len(self.series)

    @property
    def episode_count(self):
        return len(self.episodes)

    @property
    def track_count(self):
        return sum(episode.track_count for episode in self.episodes)

    @property
    def first_broadcast(self):
        return min(episode.broadcast for episode in self.episodes)

    @property
    def last_broadcast(self):
        return max(episode.broadcast for episode in self.episodes)

    def _parse(self, series: list[str | None], episodes: list[dict[str, Any]]):
        grouped: defaultdict[int, list[Episode]] = defaultdict(list)

        for item in episodes:
            episode = Episode.from_dict(item)
            grouped[episode.series].append(episode)
            self.episodes.append(episode)

        if len(series) != len(grouped):
            raise ValueError(
                f"series data has {len(series)} entries but the episode data "
                f"covers {len(grouped)} series - the two files are out of step, "
                f"so season ids would be assigned to the wrong series"
            )

        for x, item in enumerate(grouped.values(), start=1):
            self.series.append(Series(id=series[x - 1], number=x, episodes=item))


@dataclasses.dataclass
class Series:
    id: str | None
    number: int
    episodes: list["Episode"]

    def __getitem__(self, index: int):
        return self.episodes[index]

    def __iter__(self):
        return iter(self.episodes)

    def __len__(self):
        return len(self.episodes)

    @property
    def episodes_with_comments(self):
        return [
            item
            for item in self
            if item.has_episode_comments or item.has_track_comments
        ]

    @property
    def track_count(self):
        return sum(episode.track_count for episode in self)

    @property
    def duration_seconds(self):
        return sum(episode.duration_seconds for episode in self)

    @property
    def first_broadcast(self):
        return min(episode.broadcast for episode in self)

    @property
    def last_broadcast(self):
        return max(episode.broadcast for episode in self)

    @property
    def regular_presenters(self):
        # TODO: make this non-heuristic
        return self.presenters[:2]

    @property
    def presenters(self):
        """Everyone who picked a track this series; most picks first."""
        counts = defaultdict(int)

        for episode in self:
            for track in episode:
                counts[track.chosen_by] += 1

        return sorted(counts, key=lambda name: (-counts[name], name))


@dataclasses.dataclass
class Episode:
    id: str
    url: str
    playlist_tracks: list["Track"]
    series: int
    episode: int
    broadcast: str
    released: str
    duration_seconds: int
    name: str
    description: str
    image: str
    one_off_special: bool = False
    comments: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        """Build from raw JSON. Keys not listed here are ignored."""
        return cls(
            id=data["id"],
            url=data["url"],
            playlist_tracks=[
                Track.from_dict(item, number=x)
                for x, item in enumerate(data.get("playlist_tracks", []), start=1)
            ],
            series=data["series"],
            episode=data["episode"],
            broadcast=data["broadcast"],
            released=data["released"],
            duration_seconds=data["duration_seconds"],
            name=data["name"],
            description=data["description"],
            image=data["image"],
            one_off_special=data.get("one_off_special", False),
            comments=data.get("comments"),
        )

    def __getitem__(self, index: int):
        return self.playlist_tracks[index]

    def __iter__(self):
        return iter(self.playlist_tracks)

    @property
    def number(self):
        return self.episode

    @property
    def code(self):
        return f"S{self.series:02}E{self.episode:02}"

    @property
    def track_count(self):
        return len(self.playlist_tracks)

    @property
    def pickers(self):
        """Everyone who chose a track in this episode, in first-pick order."""
        names = []

        for track in self.playlist_tracks:
            if track.chosen_by not in names:
                names.append(track.chosen_by)

        return names

    @property
    def is_first(self):
        return self.episode == 1

    @property
    def has_episode_comments(self):
        return self.comments is not None

    @property
    def has_track_comments(self):
        for track in self.playlist_tracks:
            if track.has_comments:
                return True
        return False


@dataclasses.dataclass
class Track:
    _name: str
    number: int
    artist: str | None
    chosen_by: str
    spotify: "SpotifyData | None"
    youtube: str | None = None
    connection: str | None = None
    comments: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any], number: int):
        spotify = data.get("spotify")

        return cls(
            _name=data["name"],
            number=number,
            artist=data.get("artist"),
            chosen_by=data["chosen_by"],
            spotify=SpotifyData.from_dict(spotify) if spotify else None,
            youtube=data.get("youtube"),
            connection=data.get("connection"),
            comments=data.get("comments"),
        )

    @property
    def is_first(self):
        return self.number == 1

    @property
    def spotify_id(self):
        if self.spotify is not None and self.spotify.id is not None:
            return self.spotify.id
        return None

    @property
    def has_media_link(self):
        return bool(self.spotify_id or self.youtube)

    @property
    def has_comments(self):
        return self.comments is not None

    @property
    def artists(self):
        if self.spotify is not None and self.spotify.artists:
            return [artist.name for artist in self.spotify.artists]
        elif self.artist is not None:
            return [self.artist]
        return None

    @property
    def name(self):
        if self.spotify is not None and self.spotify.name is not None:
            return self.spotify.name
        else:
            return self._name

    @property
    def isrc_code(self):
        if self.spotify is not None and self.spotify.isrc is not None:
            return self.spotify.isrc
        return None

    @property
    def duration_ms(self):
        if self.spotify is not None and self.spotify.duration_ms is not None:
            return self.spotify.duration_ms
        return None

    def artwork_url(self, width: Literal[640, 300, 64] = 300):
        if self.spotify is None or self.spotify.image is None:
            return None
        else:
            return f"{SPOTIFY_IMAGE_URL}{SPOTIFY_IMAGE_PREFIXES[width]}{self.spotify.image}"


@dataclasses.dataclass
class SpotifyData:
    id: str
    url: str
    name: str
    artists: list["SpotifyArtist"]
    released: str
    image: str | None = None
    isrc: str | None = None
    duration_ms: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        artists = [SpotifyArtist(**item) for item in data.get("artists", [])]
        return cls(**{**data, "artists": artists})


@dataclasses.dataclass
class SpotifyArtist:
    id: str
    name: str


@dataclasses.dataclass
class PresenterLeaderboardRow:
    date: str
    series: int
    episode: int
    track: Track

    @property
    def name(self):
        return self.track.chosen_by

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from platypush.schemas.torrent import TorrentResultSchema


@dataclass
class TorrentSearchResult:
    """
    Data class for results returned by
    :meth:`platypush.plugins.torrent.TorrentPlugin.search`.
    """

    title: str
    file: Optional[str] = None
    url: Optional[str] = None
    provider: Optional[str] = None
    type: Optional[str] = None
    size: int = 0
    duration: float = 0
    language: Optional[str] = None
    category: Optional[str] = None
    seeds: int = 0
    peers: int = 0
    image: Optional[str] = None
    description: Optional[str] = None
    is_media: bool = False
    imdb_id: Optional[str] = None
    tvdb_id: Optional[str] = None
    year: Optional[int] = None
    created_at: Optional[datetime] = None
    quality: Optional[str] = None
    overview: Optional[str] = None
    trailer: Optional[str] = None
    genres: List[str] = field(default_factory=list)
    rating: Optional[float] = None
    critic_rating: Optional[float] = None
    community_rating: Optional[float] = None
    votes: Optional[int] = None
    series: Optional[str] = None
    season: Optional[int] = None
    episode: Optional[int] = None
    num_seasons: Optional[int] = None
    country: Optional[str] = None
    network: Optional[str] = None
    series_status: Optional[str] = None

    def to_dict(self) -> dict:
        return dict(TorrentResultSchema().dump(self))

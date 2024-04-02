from marshmallow import EXCLUDE, fields, post_dump, post_load, pre_dump, pre_load
from marshmallow.schema import Schema

from platypush.plugins.media import PlayerState
from platypush.schemas import DateTime


class MopidyTrackSchema(Schema):
    """
    Mopidy track schema.
    """

    uri = fields.String(required=True, metadata={"description": "Track URI"})
    file = fields.String(
        metadata={"description": "Track URI, for MPD compatibility purposes"}
    )
    artist = fields.String(missing=None, metadata={"description": "Artist name"})
    title = fields.String(missing=None, metadata={"description": "Track title"})
    album = fields.String(missing=None, metadata={"description": "Album name"})
    artist_uri = fields.String(
        missing=None, metadata={"description": "Artist URI (if available)"}
    )
    album_uri = fields.String(
        missing=None, metadata={"description": "Album URI (if available)"}
    )
    time = fields.Float(
        missing=None, metadata={"description": "Track length (in seconds)"}
    )
    playlist_pos = fields.Integer(
        missing=None,
        metadata={"description": "Track position in the tracklist/playlist"},
    )
    track_id = fields.Integer(
        missing=None, metadata={"description": "Track ID in the current tracklist"}
    )
    track_no = fields.Integer(
        missing=None, metadata={"description": "Track number in the album"}
    )
    date = fields.String(missing=None, metadata={"description": "Track release date"})
    genre = fields.String(missing=None, metadata={"description": "Track genre"})
    type = fields.Constant("track", metadata={"description": "Item type"})

    @pre_load
    def parse(self, track: dict, **_):
        from platypush.plugins.music.mopidy import EmptyTrackException

        uri = (track or {}).get("uri", (track or {}).get("track", {}).get("uri"))
        if not uri:
            raise EmptyTrackException("Empty track")

        tlid = track.get("tlid")
        playlist_pos = track.get("playlist_pos")
        if track.get("track"):
            track = track.get("track", {})

        length = track.get("length", track.get("time", track.get("duration")))
        return {
            "uri": uri,
            "artist": next(
                iter(item.get("name") for item in track.get("artists", [])),
                None,
            ),
            "title": track.get("name"),
            "album": track.get("album", {}).get("name"),
            "artist_uri": next(
                iter(item.get("uri") for item in track.get("artists", [])), None
            ),
            "album_uri": track.get("album", {}).get("uri"),
            "time": length / 1000 if length is not None else None,
            "playlist_pos": (
                track.get("playlist_pos") if playlist_pos is None else playlist_pos
            ),
            "date": track.get("date", track.get("album", {}).get("date")),
            "track_id": tlid,
            "track_no": track.get("track_no"),
            "genre": track.get("genre"),
        }

    @post_dump
    def to_dict(self, track: dict, **_):
        """
        Fill/move missing fields in the dictionary.
        """
        return {
            "file": track["uri"],
            **track,
        }


class MopidyStatusSchema(Schema):
    """
    Mopidy status schema.
    """

    state = fields.Enum(
        PlayerState,
        required=True,
        metadata={"description": "Player state"},
    )
    volume = fields.Float(metadata={"description": "Player volume (0-100)"})
    consume = fields.Boolean(metadata={"description": "Consume mode"})
    random = fields.Boolean(metadata={"description": "Random mode"})
    repeat = fields.Boolean(metadata={"description": "Repeat mode"})
    single = fields.Boolean(metadata={"description": "Single mode"})
    mute = fields.Boolean(metadata={"description": "Mute mode"})
    time = fields.Float(metadata={"description": "Current time (in seconds)"})
    playing_pos = fields.Integer(
        metadata={"description": "Index of the currently playing track"}
    )
    track = fields.Nested(
        MopidyTrackSchema, missing=None, metadata={"description": "Current track"}
    )

    @post_dump
    def post_dump(self, data: dict, **_):
        """
        Post-dump hook.
        """
        state = data.get("state")
        if state:
            data["state"] = getattr(PlayerState, state).value
        return data


class MopidyPlaylistSchema(Schema):
    """
    Mopidy playlist schema.
    """

    # pylint: disable=too-few-public-methods
    class Meta:  # type: ignore
        """
        Mopidy playlist schema metadata.
        """

        unknown = EXCLUDE

    uri = fields.String(required=True, metadata={"description": "Playlist URI"})
    name = fields.String(required=True, metadata={"description": "Playlist name"})
    last_modified = DateTime(metadata={"description": "Last modified timestamp"})
    tracks = fields.List(
        fields.Nested(MopidyTrackSchema),
        missing=None,
        metadata={"description": "Playlist tracks"},
    )
    type = fields.Constant("playlist", metadata={"description": "Item type"})

    @pre_dump
    def pre_dump(self, playlist, **_):
        """
        Pre-dump hook.
        """
        last_modified = (
            playlist.last_modified
            if hasattr(playlist, "last_modified")
            else playlist.get("last_modified")
        )

        if last_modified:
            last_modified /= 1000
        if hasattr(playlist, "last_modified"):
            playlist.last_modified = last_modified
        else:
            playlist["last_modified"] = last_modified

        return playlist


class MopidyArtistSchema(Schema):
    """
    Mopidy artist schema.
    """

    uri = fields.String(required=True, metadata={"description": "Artist URI"})
    file = fields.String(
        metadata={"description": "Artist URI, for MPD compatibility purposes"}
    )
    name = fields.String(missing=None, metadata={"description": "Artist name"})
    artist = fields.String(
        missing=None,
        metadata={"description": "Same as name - for MPD compatibility purposes"},
    )
    type = fields.Constant("artist", metadata={"description": "Item type"})

    @post_dump
    def to_dict(self, artist: dict, **_):
        """
        Fill/move missing fields in the dictionary.
        """
        return {
            "file": artist["uri"],
            "artist": artist["name"],
            **artist,
        }


class MopidyAlbumSchema(Schema):
    """
    Mopidy album schema.
    """

    uri = fields.String(required=True, metadata={"description": "Album URI"})
    file = fields.String(
        metadata={"description": "Artist URI, for MPD compatibility purposes"}
    )
    artist = fields.String(missing=None, metadata={"description": "Artist name"})
    album = fields.String(
        missing=None,
        metadata={"description": "Same as name - for MPD compatibility purposes"},
    )
    name = fields.String(missing=None, metadata={"description": "Album name"})
    artist_uri = fields.String(missing=None, metadata={"description": "Artist URI"})
    date = fields.String(missing=None, metadata={"description": "Album release date"})
    genre = fields.String(missing=None, metadata={"description": "Album genre"})

    def parse(self, data: dict, **_):
        assert data.get("uri"), "Album URI is required"
        return {
            "uri": data["uri"],
            "artist": data.get("artist")
            or next(
                iter(item.get("name") for item in data.get("artists", [])),
                None,
            ),
            "name": data.get("name"),
            "artist_uri": data.get("artist_uri")
            or next(iter(item.get("uri") for item in data.get("artists", [])), None),
            "album_uri": data.get("album_uri") or data.get("album", {}).get("uri"),
            "date": data.get("date", data.get("album", {}).get("date")),
            "genre": data.get("genre"),
        }

    @pre_load
    def pre_load(self, album: dict, **_):
        """
        Pre-load hook.
        """
        return self.parse(album)

    @pre_dump
    def pre_dump(self, album: dict, **_):
        """
        Pre-dump hook.
        """
        return self.parse(album)

    @post_dump
    def to_dict(self, album: dict, **_):
        """
        Fill/move missing fields in the dictionary.
        """
        return {
            "file": album["uri"],
            "album": album["name"],
            **album,
        }


class MopidyDirectorySchema(Schema):
    """
    Mopidy directory schema.
    """

    uri = fields.String(required=True, metadata={"description": "Directory URI"})
    name = fields.String(required=True, metadata={"description": "Directory name"})
    type = fields.Constant("directory", metadata={"description": "Item type"})


class MopidyFilterSchema(Schema):
    """
    Mopidy filter schema.
    """

    uris = fields.List(fields.String, metadata={"description": "Filter by URIs"})
    artist = fields.List(fields.String, metadata={"description": "Artist name(s)"})
    album = fields.List(fields.String, metadata={"description": "Album name(s)"})
    title = fields.List(fields.String, metadata={"description": "Track title(s)"})
    albumartist = fields.List(
        fields.String, metadata={"description": "Album artist name(s)"}
    )
    date = fields.List(fields.String, metadata={"description": "Track release date(s)"})
    genre = fields.List(fields.String, metadata={"description": "Genre(s)"})
    comment = fields.List(fields.String, metadata={"description": "Comment(s)"})
    disc_no = fields.List(fields.Integer, metadata={"description": "Disc number(s)"})
    musicbrainz_artistid = fields.List(
        fields.String, metadata={"description": "MusicBrainz artist ID(s)"}
    )
    musicbrainz_albumid = fields.List(
        fields.String, metadata={"description": "MusicBrainz album ID(s)"}
    )
    musicbrainz_trackid = fields.List(
        fields.String, metadata={"description": "MusicBrainz album artist ID(s)"}
    )
    any = fields.List(
        fields.String, metadata={"description": "Generic search string(s)"}
    )

    @pre_load
    def pre_load(self, data: dict, **_):
        """
        Pre-load hook.
        """
        for field_name, field in self.fields.items():
            value = data.get(field_name)

            # Back-compatibtility with MPD's single-value filters
            if (
                value is not None
                and isinstance(field, fields.List)
                and isinstance(value, str)
            ):
                data[field_name] = [value]

        return data

    @post_load
    def post_load(self, data: dict, **_):
        """
        Post-load hook.
        """
        title = data.pop("title", None)
        if title:
            data["track_name"] = title

        return data

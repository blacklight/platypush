<template>
  <Loading v-if="loading" />
  <MusicPlugin :plugin-name="pluginName"
               :config="config"
               :edited-playlist-tracks="editedPlaylistTracks"
               :edited-playlist="editedPlaylist"
               :images="images"
               :library-results="libraryResults"
               :loading="loading"
               :path="path"
               :playlists="playlists"
               :search-results="searchResults"
               :status="status"
               :track="track"
               :track-info="trackInfo"
               :tracks="tracks"
               @add-to-playlist="addToPlaylist"
               @add-to-tracklist-from-edited-playlist="addToTracklistFromEditedPlaylist"
               @add-to-tracklist="addToTracklist"
               @cd="cd"
               @clear="clear"
               @consume="consume"
               @info="trackInfo = $event"
               @load-playlist="loadPlaylist"
               @new-playing-track="refreshStatus(true, true, $event)"
               @next="next"
               @pause="pause"
               @play-playlist="playPlaylist"
               @play="play"
               @playlist-add="playlistAdd"
               @playlist-edit="playlistEditChanged"
               @playlist-track-move="playlistTrackMove"
               @playlist-update="refresh(true)"
               @previous="previous"
               @random="random"
               @remove-from-playlist="removeFromPlaylist"
               @remove-from-tracklist="removeFromTracklist"
               @remove-playlist="removePlaylist"
               @repeat="repeat"
               @search-clear="searchResults = []"
               @search="search"
               @seek="seek"
               @set-volume="setVolume"
               @status-update="refreshStatus(true, true, $event)"
               @stop="stop"
               @swap-tracks="swapTracks"
               @tracklist-move="moveTracklistTracks"
               @tracklist-save="saveToPlaylist" />
</template>

<script>
import MusicPlugin from "@/components/panels/Music/Index"
import Utils from "@/Utils"
import Loading from "@/components/Loading"
import Status from "@/mixins/Music/Status";
import { bus } from "@/bus";

export default {
  components: {Loading, MusicPlugin},
  mixins: [Status, Utils],
  props: {
    config: {
      type: Object,
      default: () => {},
    },

    pluginName: {
      type: String,
      required: true,
    },

    fetchStatusOnUpdate: {
      type: Boolean,
      default: true,
    },
  },

  data() {
    return {
      loading: false,
      tracks: [],
      playlists: [],
      status_: {},
      images: {},
      editedPlaylist: null,
      editedPlaylistTracks: [],
      trackInfo: null,
      searchResults: [],
      libraryResults: [],
      path: [],
    }
  },

  computed: {
    status() {
      const status = {...this.status_}
      // This is the standard case for new integrations, where elapsed isn't
      // reported and time is not a string in the format `elapsed:duration`.
      // In this case, time is elapsed time.
      if (!status.elapsed && !isNaN(parseFloat(status.time)))
        status.elapsed = status.time

      return status
    },

    track() {
      let pos = null
      if (this.status?.playingPos != null)
        pos = this.status.playingPos
      else if (this.status?.track?.pos != null)
        pos = this.status.track.pos

      if (pos == null)
        return null

      return this.tracks[pos]
    }
  },

  methods: {
    async refreshTracks(background) {
      if (!background)
        this.loading = true

      try {
        this.tracks = await this.request(`${this.pluginName}.get_tracks`)
      } finally {
        this.loading = false
      }
    },

    setStatusFromEvent(event) {
      if (!event)
        return

      if (event.status)
        this.status_ = this.parseStatus(event.status)
    },

    async refreshStatus(background, isStatusUpdate, event) {
      if (isStatusUpdate && !this.fetchStatusOnUpdate) {
        this.setStatusFromEvent(event)
      } else {
        if (!background)
          this.loading = true

        try {
          this.status_ = this.parseStatus(await this.request(`${this.pluginName}.status`))
        } finally {
          this.loading = false
        }
      }

      this.refreshCurrentImage()
    },

    async refreshCurrentImage() {
      const curTrack = this.track?.uri || this.track?.file
      if (!curTrack || curTrack in this.images)
        return

      await this.refreshImages([this.track])
    },

    async refreshImages(tracks) {
      Object.entries(
        await this.request(
          `${this.pluginName}.get_images`, {
            resources: [
              ...new Set(
                tracks
                .map((track) => track.uri || track.file)
                .filter((uri) => uri && !(uri in this.images))
              )
            ]
          }
        )
      ).forEach(([uri, image]) => {
        this.images[uri] = image
      })
    },

    async refreshPlaylists(background) {
      if (!background)
        this.loading = true

      try {
        this.playlists = (await this.request(`${this.pluginName}.get_playlists`)).map((playlist) => {
          return {
            ...playlist,
            lastModified: playlist.last_modified,
          }
        }).sort((a, b) => a.name.localeCompare(b.name))
      } finally {
        this.loading = false
      }
    },

    async refresh(background) {
      if (!background)
        this.loading = true

      try {
        await Promise.all([
          this.refreshTracks(background),
          this.refreshStatus(background),
          this.refreshPlaylists(background),
        ])
      } finally {
        this.loading = false
      }
    },

    async play(event) {
      if (event?.pos != null) {
        await this.request(`${this.pluginName}.play_pos`, {pos: event.pos})
      } else if (event?.file) {
        await this.request(`${this.pluginName}.play`, {resource: event.file})
      } else {
        await this.request(`${this.pluginName}.play`)
      }

      await this.refreshStatus(true)
    },

    async pause() {
      await this.request(`${this.pluginName}.pause`)
      await this.refreshStatus(true)
    },

    async stop() {
      await this.request(`${this.pluginName}.stop`)
      await this.refreshStatus(true)
    },

    async previous() {
      await this.request(`${this.pluginName}.previous`)
      await this.refreshStatus(true)
    },

    async next() {
      await this.request(`${this.pluginName}.next`)
      await this.refreshStatus(true)
    },

    async clear() {
      await this.request(`${this.pluginName}.clear`)
      await Promise.all([this.refreshStatus(true), this.refreshTracks(true)])
    },

    async setVolume(volume) {
      if (volume === this.status.volume)
        return

      await this.request(`${this.pluginName}.set_volume`, {volume: volume})
      await this.refreshStatus(true)
    },

    async seek(pos) {
      await this.request(`${this.pluginName}.seek`, {position: pos})
      await this.refreshStatus(true)
    },

    async repeat(value) {
      await this.request(`${this.pluginName}.repeat`, {value: !!parseInt(+value)})
      await this.refreshStatus(true)
    },

    async random(value) {
      await this.request(`${this.pluginName}.random`, {value: !!parseInt(+value)})
      await this.refreshStatus(true)
    },

    async consume(value) {
      await this.request(`${this.pluginName}.consume`, {value: !!parseInt(+value)})
      await this.refreshStatus(true)
    },

    async addToTracklist(resource) {
      if (resource.file)
        resource = resource.file

      await this.request(`${this.pluginName}.add`, {resource: resource})
      await this.refresh(true)
    },

    async addToTracklistFromEditedPlaylist(event) {
      const tracks = event?.tracks?.map(
        (pos) => this.editedPlaylistTracks[pos]
      )?.filter((track) => track?.file)?.map((track) => track.file)

      if (!tracks?.length)
        return

      await Promise.all(tracks.map((track) => this.request(`${this.pluginName}.add`, {resource: track})))
      await this.refresh(true)

      if (event.play)
        await this.request(`${this.pluginName}.play_pos`, {pos: this.tracks.length - tracks.length})
    },

    async removeFromPlaylist(positions) {
      await this.request(
        `${this.pluginName}.remove_from_playlist`,
          {resources: positions, playlist: this.playlists[this.editedPlaylist].name}
      )
      await this.playlistEditChanged(this.editedPlaylist)
    },

    async removeFromTracklist(positions) {
      await this.request(`${this.pluginName}.delete`, {positions: positions.sort()})
      await this.refresh(true)
    },

    async swapTracks(positions) {
      await this.request(`${this.pluginName}.move`, {from_pos: positions[0], to_pos: positions[1]})
      await this.refresh(true)
    },

    async playPlaylist(position) {
      await this._loadPlaylist(position, true)
    },

    async loadPlaylist(position) {
      await this._loadPlaylist(position, false)
    },

    async _loadPlaylist(position, play) {
      const playlist = this.playlists[position]
      await this.request(
        `${this.pluginName}.load`, {
          playlist: (playlist.uri || playlist.name), play: play
        }
      )
      await this.refresh(true)
    },

    async removePlaylist(position) {
      const playlist = this.playlists[position]
      if (!confirm(`Are you REALLY sure that you want to remove the playlist ${playlist.name}?`))
        return

      await this.request(`${this.pluginName}.delete_playlist`, {playlist: playlist.name})
      await this.refreshPlaylists(true)
    },

    async saveToPlaylist(name) {
      await this.request(`${this.pluginName}.save`, {name: name})
      await this.refreshPlaylists(true)
    },

    splitMoveTracksIntoChunks(event) {
      // Split the selected source tracks into chunks containing consecutive
      // tracks, since the music plugin move API exposes `start`, `end` and
      // `position` parameters.
      let chunk = [];
      let offset = event.to;
      const chunks = (event?.from || [])
        .map((i) => parseInt(i))
        .sort((a, b) => a - b)
        .reduce((acc, pos, idx) => {
          if (idx === 0 || (chunk.length > 0 && pos === chunk[chunk.length - 1] + 1)) {
            chunk.push(pos)
          } else {
            acc.push(chunk)
            chunk = [pos]
          }

          return acc
        }, [])

      if (chunk.length > 0)
        chunks.push(chunk)

      return chunks.map((chunk) => {
        const start = chunk[0]
        const end = chunk[chunk.length - 1] === chunk[0] ? chunk[0] : chunk[chunk.length - 1] + 1
        let ret = {
            start: start,
            end: end,
            position: offset,
        }

        offset += chunk.length
        return ret
      })
    },

    async moveTracklistTracks(event) {
      for (const chunk of this.splitMoveTracksIntoChunks(event)) {
        await this.request(`${this.pluginName}.move`, chunk)
      }

      if (!this.fetchStatusOnUpdate)
        await this.refreshTracks(true)
    },

    async playlistAdd(track) {
      await this.request(
        `${this.pluginName}.add_to_playlist`,
        {resources: [track], playlist: this.playlists[this.editedPlaylist].name}
      )
      await this.playlistEditChanged(this.editedPlaylist)
    },

    async playlistEditChanged(playlist) {
      this.editedPlaylist = playlist
      if (playlist == null)
        return

      this.loading = true
      try {
        this.editedPlaylistTracks = await this.request(
          `${this.pluginName}.get_playlist`,
            {playlist: this.playlists[playlist].name}
        )
      } finally {
        this.loading = false
      }
    },

    async addToPlaylist(event) {
      await Promise.all(event.playlists.map(async (playlistIdx) => {
        await this.request(`${this.pluginName}.add_to_playlist`, {
          resources: [event.track.file],
          playlist: this.playlists[playlistIdx].name
        })

        await this.playlistEditChanged(playlistIdx)
      }))
    },

    async playlistTrackMove(event) {
      const playlist = this.playlists[event.playlist]
      if (!playlist)
        return

      for (const chunk of this.splitMoveTracksIntoChunks(event)) {
        await this.request(
          `${this.pluginName}.playlist_move`, {
            playlist: playlist.uri || playlist.name,
            start: chunk.start,
            end: chunk.end,
            position: chunk.position,
          }
        )
      }

      await this.playlistEditChanged(event.playlist)
    },

    async search(query) {
      this.loading = true

      try {
        this.searchResults = await this.request(`${this.pluginName}.search`, {filter: query})
      } finally {
        this.loading = false
      }
    },

    async cd(path) {
      this.loading = true

      let uri = path
      if (Array.isArray(path))
        uri = path.length === 0 ? null : path[path.length - 1]

      try {
        this.libraryResults = (
          await this.request(`${this.pluginName}.browse`, {uri: uri})
        ).filter((result) => !result.playlist)

        this.path = path
      } finally {
        this.loading = false
      }
    },
  },

  mounted() {
    bus.on('connected', this.refresh)
    this.refresh()
    this.cd(this.path)
  },
}
</script>

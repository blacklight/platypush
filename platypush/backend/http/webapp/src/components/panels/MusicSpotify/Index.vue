<template>
  <Loading v-if="loading" />
  <MusicPlugin plugin-name="music.spotify" :loading="loading" :config="config" :tracks="tracks" :status="status"
               :playlists="playlists" :edited-playlist="editedPlaylist" :edited-playlist-tracks="editedPlaylistTracks"
               :track-info="trackInfo" :search-results="searchResults" :library-results="libraryResults" :path="path"
               :devices="devices" :selected-device="selectedDevice" :active-device="activeDevice" @play="play"
               @pause="pause" @stop="stop" @previous="previous" @next="next" @clear="clear" @set-volume="setVolume"
               @seek="seek" @consume="consume" @random="random" @repeat="repeat" @status-update="refreshStatus(true)"
               @new-playing-track="refreshStatus(true)" @remove-from-tracklist="removeFromTracklist"
               @add-to-tracklist="addToTracklist" @swap-tracks="swapTracks" @load-playlist="loadPlaylist"
               @play-playlist="playPlaylist" @remove-playlist="removePlaylist" @tracklist-move="moveTracklistTracks"
               @tracklist-save="saveToPlaylist" @playlist-edit="playlistEditChanged" @refresh-status="refreshStatus"
               @add-to-tracklist-from-edited-playlist="addToTracklistFromEditedPlaylist"
               @remove-from-playlist="removeFromPlaylist" @info="trackInfo = $event" @playlist-add="playlistAdd"
               @add-to-playlist="addToPlaylist" @playlist-track-move="playlistTrackMove" @search="search"
               @search-clear="searchResults = []" @cd="cd" @playlist-update="refresh(true)"
               @select-device="selectDevice" />
</template>

<script>
import MusicPlugin from "@/components/panels/Music/Index";
import Utils from "@/Utils";
import Loading from "@/components/Loading";

export default {
  name: "MusicSpotify",
  components: {Loading, MusicPlugin},
  mixins: [Utils],
  props: {
    config: {
      type: Object,
      default: () => {},
    },
  },

  data() {
    return {
      loading: false,
      devices: {},
      selectedDevice: null,
      activeDevice: null,
      tracks: [],
      playlists: [],
      status: {},
      editedPlaylist: null,
      editedPlaylistTracks: [],
      trackInfo: null,
      searchResults: [],
      libraryResults: [],
      path: '/',
    }
  },

  methods: {
    async refreshTracks(background) {
      if (!background)
        this.loading = true

      try {
        this.tracks = (await this.request('music.spotify.history')).map((track) => {
          track.time = track.duration
          return track
        })
      } finally {
        this.loading = false
      }
    },

    async refreshStatus(background) {
      if (!background)
        this.loading = true

      this.devices = (await this.request('music.spotify.get_devices')).reduce((obj, device) => {
        obj[device.id] = device
        return obj
      }, {})

      const activeDevices = Object.values(this.devices).filter((device) => device.is_active)
      this.activeDevice = activeDevices.length ? activeDevices[0].id : null
      if (!this.selectedDevice && Object.values(this.devices).length)
        this.selectedDevice = this.activeDevice || [...Object.values(this.devices)][0].id

      try {
        const status = await this.request('music.spotify.status')
        this.status = {
          ...status,
          duration: status.time,
        }
      } finally {
        this.loading = false
      }

      if (this.status.track) {
        if (this.tracks?.[0]?.id !== this.status.track.id)
          this.tracks = [{
            ...this.status.track,
            time: this.status.duration,
          }, ...this.tracks]
        this.status.playingPos = 0
      }
    },

    async refreshPlaylists(background) {
      if (!background)
        this.loading = true

      try {
        this.playlists = (await this.request('music.spotify.get_playlists'))
            .sort((a, b) => a.name.localeCompare(b.name))
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
      if (event?.pos != null)
        event.uri = this.tracks[event.pos].uri

      if (event?.uri) {
        await this.request('music.spotify.play', {
          resource: event.uri,
          device: this.selectedDevice,
        })
      } else {
        await this.request('music.spotify.play', {
          device: this.selectedDevice,
        })
      }

      await this.refreshStatus(true)
    },

    async pause() {
      await this.request('music.spotify.pause', {
        device: this.selectedDevice,
      })
      await this.refreshStatus(true)
    },

    async stop() {
      await this.request('music.spotify.stop', {
        device: this.selectedDevice,
      })
      await this.refreshStatus(true)
    },

    async previous() {
      await this.request('music.spotify.previous', {
        device: this.selectedDevice,
      })
      await this.refreshStatus(true)
    },

    async next() {
      await this.request('music.spotify.next', {
        device: this.selectedDevice,
      })
      await this.refreshStatus(true)
    },

    async clear() {},

    async setVolume(volume) {
      if (volume === this.status.volume)
        return

      await this.request('music.spotify.set_volume', {
        device: this.selectedDevice,
        volume: volume,
      })
      await this.refreshStatus(true)
    },

    async seek(pos) {
      await this.request('music.spotify.seek', {
        device: this.selectedDevice,
        position: pos,
      })
      await this.refreshStatus(true)
    },

    async repeat() {
      await this.request('music.spotify.repeat', {
        device: this.selectedDevice,
        value: !this.status?.repeat,
      })
      await this.refreshStatus(true)
    },

    async random() {
      await this.request('music.spotify.random', {
        device: this.selectedDevice,
        value: !this.status?.random,
      })
      await this.refreshStatus(true)
    },

    async consume() {},

    async addToTracklist(resource) {
      if (resource.file)
        resource = resource.file

      await this.request('music.spotify.add', {
        device: this.selectedDevice,
        resource: resource,
      })
      await this.refresh(true)
    },

    async addToTracklistFromEditedPlaylist(event) {
      const track = this.editedPlaylistTracks[event.pos]
      if (!track)
        return

      const method = event.play ? 'play' : 'add'
      await this.request(`music.spotify.${method}`, {
        device: this.selectedDevice,
        resource: track.uri
      })
      await this.refresh(true)
    },

    async removeFromPlaylist(positions) {
      const tracks = positions.map((pos) => this.playlists[this.editedPlaylist].tracks[pos].uri)
      await this.request('music.spotify.remove_from_playlist',
          {resources: tracks, playlist: this.playlists[this.editedPlaylist].name})
      await this.playlistEditChanged(this.editedPlaylist)
    },

    async removeFromTracklist() {},
    async swapTracks() {},

    async playPlaylist(position) {
      await this._loadPlaylist(position, true)
    },

    async loadPlaylist(position) {
      await this._loadPlaylist(position, false)
    },

    async _loadPlaylist(position) {
      const playlist = this.playlists[position]
      await this.request('music.spotify.play', {
        resource: playlist.uri,
        device: this.selectedDevice,
      })
      await this.refresh(true)
    },

    async removePlaylist() {
      this.notify({
        text: 'Playlist removal is not supported'
      })
    },

    async saveToPlaylist() {},
    async moveTracklistTracks() {},

    async playlistAdd(track) {
      await this.request('music.spotify.add_to_playlist', {
        resources: [track],
        playlist: this.playlists[this.editedPlaylist].uri
      })

      await this.playlistEditChanged(this.editedPlaylist)
    },

    async playlistEditChanged(playlist) {
      this.editedPlaylist = playlist
      if (playlist == null)
        return

      this.loading = true
      try {
        const list = await this.request('music.spotify.get_playlist', {
          playlist: this.playlists[playlist].uri
        })

        this.editedPlaylistTracks = list.tracks.map((track) => {
          track.time = track.duration
          return track
        })
      } finally {
        this.loading = false
      }
    },

    async addToPlaylist(event) {
      await Promise.all(event.playlists.map(async (playlistIdx) => {
        await this.request('music.spotify.add_to_playlist', {
          resources: [event.track.uri],
          playlist: this.playlists[playlistIdx].uri
        })

        await this.playlistEditChanged(playlistIdx)
      }))
    },

    async playlistTrackMove(event) {
      await this.request('music.spotify.playlist_move', {
        playlist: this.playlists[event.playlist].uri,
        from_pos: event.from-1,
        to_pos: event.to-1,
      })

      await this.playlistEditChanged(event.playlist)
    },

    async search(query) {
      this.loading = true

      try {
        this.searchResults = (await this.request('music.spotify.search', query)).map((item) => {
          item.time = item.duration
          return item
        })
      } finally {
        this.loading = false
      }
    },

    async cd() {},

    async selectDevice(deviceId) {
      if (this.selectedDevice === deviceId)
        return

      await this.request('music.spotify.start_or_transfer_playback', {
        device: deviceId,
      })

      this.selectedDevice = deviceId
      this.refreshStatus(true)
    },
  },

  mounted() {
    this.refresh()
  },
}
</script>

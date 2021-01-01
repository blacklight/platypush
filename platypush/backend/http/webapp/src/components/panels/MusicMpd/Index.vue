<template>
  <Loading v-if="loading" />
  <MusicPlugin plugin-name="music.mpd" :loading="loading" :config="config" :tracks="tracks" :status="status"
               :playlists="playlists" :edited-playlist="editedPlaylist" :edited-playlist-tracks="editedPlaylistTracks"
               :track-info="trackInfo" :search-results="searchResults" @play="play" @pause="pause" @stop="stop"
               @previous="previous" @next="next" @clear="clear" @set-volume="setVolume" @seek="seek" @consume="consume"
               @random="random" @repeat="repeat" @status-update="refreshStatus(true)"
               @playlist-update="refresh(true)" @new-playing-track="refreshStatus(true)"
               @remove-from-tracklist="removeFromTracklist" @add-to-tracklist="addToTracklist" @swap-tracks="swapTracks"
               @load-playlist="loadPlaylist" @play-playlist="playPlaylist" @remove-playlist="removePlaylist"
               @tracklist-move="moveTracklistTracks" @tracklist-save="saveToPlaylist"
               @playlist-edit="playlistEditChanged"
               @add-to-tracklist-from-edited-playlist="addToTracklistFromEditedPlaylist"
               @remove-from-playlist="removeFromPlaylist" @info="trackInfo = $event" @playlist-add="playlistAdd"
               @add-to-playlist="addToPlaylist" @playlist-track-move="playlistTrackMove" @search="search"
               @search-clear="searchResults = []" />
</template>

<script>
import MusicPlugin from "@/components/panels/Music/Index";
import Utils from "@/Utils";
import Loading from "@/components/Loading";

export default {
  name: "MusicMpd",
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
      tracks: [],
      playlists: [],
      status: {},
      editedPlaylist: null,
      editedPlaylistTracks: [],
      trackInfo: null,
      searchResults: [],
    }
  },

  methods: {
    async refreshTracks(background) {
      if (!background)
        this.loading = true

      try {
        this.tracks = await this.request('music.mpd.playlistinfo')
      } finally {
        this.loading = false
      }
    },

    async refreshStatus(background) {
      if (!background)
        this.loading = true

      try {
        this.status = Object.entries(await this.request('music.mpd.status')).reduce((obj, [k, v]) => {
          switch (k) {
            case 'bitrate':
            case 'volume':
              obj[k] = parseInt(v)
              break

            case 'consume':
            case 'random':
            case 'repeat':
            case 'single':
              obj[k] = !!parseInt(v)
              break

            case 'song':
              obj['playingPos'] = parseInt(v)
              break

            case 'time':
              [obj['elapsed'], obj['duration']] = v.split(':').map(t => parseInt(t))
              break

            case 'elapsed':
              break

            default:
              obj[k] = v
              break
          }

          return obj
        }, {})
      } finally {
        this.loading = false
      }
    },

    async refreshPlaylists(background) {
      if (!background)
        this.loading = true

      try {
        this.playlists = (await this.request('music.mpd.listplaylists')).map((playlist) => {
          return {
            name: playlist.playlist,
            lastModified: playlist['last-modified'],
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
        await this.request('music.mpd.play_pos', {pos: event.pos})
      } else if (event.file) {
        await this.request('music.mpd.play', {resource: event.file})
      } else {
        await this.request('music.mpd.play')
      }

      await this.refreshStatus(true)
    },

    async pause() {
      await this.request('music.mpd.pause')
      await this.refreshStatus(true)
    },

    async stop() {
      await this.request('music.mpd.stop')
      await this.refreshStatus(true)
    },

    async previous() {
      await this.request('music.mpd.previous')
      await this.refreshStatus(true)
    },

    async next() {
      await this.request('music.mpd.next')
      await this.refreshStatus(true)
    },

    async clear() {
      await this.request('music.mpd.clear')
      await Promise.all([this.refreshStatus(true), this.refreshTracks(true)])
    },

    async setVolume(volume) {
      if (volume === this.status.volume)
        return

      await this.request('music.mpd.set_volume', {volume: volume})
      await this.refreshStatus(true)
    },

    async seek(pos) {
      await this.request('music.mpd.seek', {position: pos})
      await this.refreshStatus(true)
    },

    async repeat(value) {
      await this.request('music.mpd.repeat', {value: parseInt(+value)})
      await this.refreshStatus(true)
    },

    async random(value) {
      await this.request('music.mpd.random', {value: parseInt(+value)})
      await this.refreshStatus(true)
    },

    async consume(value) {
      await this.request('music.mpd.consume', {value: parseInt(+value)})
      await this.refreshStatus(true)
    },

    async addToTracklist(resource) {
      if (resource.file)
        resource = resource.file

      await this.request('music.mpd.add', {resource: resource})
      await this.refresh(true)
    },

    async addToTracklistFromEditedPlaylist(event) {
      const track = this.editedPlaylistTracks[event.pos]
      if (!track)
        return

      await this.request('music.mpd.add', {resource: track.file})
      await this.refresh(true)

      if (event.play)
        await this.request('music.mpd.play_pos', {pos: this.tracks.length-1})
    },

    async removeFromPlaylist(positions) {
      await this.request('music.mpd.playlistdelete',
          {pos: positions, name: this.playlists[this.editedPlaylist].name})
      await this.playlistEditChanged(this.editedPlaylist)
    },

    async removeFromTracklist(positions) {
      await this.request('music.mpd.delete', {positions: positions.sort()})
      await this.refresh(true)
    },

    async swapTracks(positions) {
      await this.request('music.mpd.move', {from_pos: positions[0], to_pos: positions[1]})
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
      await this.request('music.mpd.load', {playlist: playlist.name, play: play})
      await this.refresh(true)
    },

    async removePlaylist(position) {
      const playlist = this.playlists[position]
      if (!confirm(`Are you REALLY sure that you want to remove the playlist ${playlist.name}?`))
        return

      await this.request('music.mpd.rm', {playlist: playlist.name})
      await this.refreshPlaylists(true)
    },

    async saveToPlaylist(name) {
      await this.request('music.mpd.save', {name: name})
      await this.refreshPlaylists(true)
    },

    async moveTracklistTracks(event) {
      await this.request('music.mpd.move', {from_pos: event.from, to_pos: event.to})
      await this.refreshTracks(true)
    },

    async playlistAdd(track) {
      await this.request('music.mpd.playlistadd', {uri: track, name: this.playlists[this.editedPlaylist].name})
      await this.playlistEditChanged(this.editedPlaylist)
    },

    async playlistEditChanged(playlist) {
      this.editedPlaylist = playlist
      if (playlist == null)
        return

      this.loading = true
      try {
        this.editedPlaylistTracks = await this.request('music.mpd.listplaylistinfo',
            {name: this.playlists[playlist].name})
      } finally {
        this.loading = false
      }
    },

    async addToPlaylist(event) {
      await Promise.all(event.playlists.map(async (playlistIdx) => {
        await this.request('music.mpd.playlistadd', {
          uri: event.track.file,
          name: this.playlists[playlistIdx].name
        })

        await this.playlistEditChanged(playlistIdx)
      }))
    },

    async playlistTrackMove(event) {
      await this.request('music.mpd.playlistmove', {
        name: this.playlists[event.playlist].name,
        from_pos: event.from,
        to_pos: event.to,
      })

      await this.playlistEditChanged(event.playlist)
    },

    async search(query) {
      this.loading = true

      try {
        this.searchResults = await this.request('music.mpd.search', {filter: query})
      } finally {
        this.loading = false
      }
    },
  },

  mounted() {
    this.refresh()
  },
}
</script>

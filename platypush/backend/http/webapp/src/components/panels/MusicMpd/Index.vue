<template>
  <Loading v-if="loading" />
  <MusicPlugin plugin-name="music.mpd" :loading="loading" :config="config" :tracks="tracks" :status="status"
               @play="play" @pause="pause" @stop="stop" @previous="previous" @next="next" @clear="clear"
               @set-volume="setVolume" @seek="seek" @consume="consume" @random="random" @repeat="repeat"
               @status-update="refreshStatus(true)" @playlist-update="refreshTracks(true)"
               @new-playing-track="refreshStatus(true)" />
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
      status: {},
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

    async refresh(background) {
      if (!background)
        this.loading = true

      try {
        await Promise.all([this.refreshTracks(background), this.refreshStatus(background)])
      } finally {
        this.loading = false
      }
    },

    async play(event) {
      if (event?.pos != null) {
        await this.request('music.mpd.play_pos', {pos: event.pos})
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
      await this.request('music.mpd.repeat', {value: value})
      await this.refreshStatus(true)
    },

    async random(value) {
      await this.request('music.mpd.random', {value: value})
      await this.refreshStatus(true)
    },

    async consume(value) {
      await this.request('music.mpd.consume', {value: value})
      await this.refreshStatus(true)
    },
  },

  mounted() {
    this.refresh()
  },
}
</script>

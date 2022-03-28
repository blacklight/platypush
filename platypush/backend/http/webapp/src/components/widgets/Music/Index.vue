<template>
  <Loading v-if="loading" />
  <div class="music" v-else>
    <div class="track">
      <div class="unknown" v-if="!status">[Unknown state]</div>
      <div class="no-track" v-if="status && status.state === 'stop'">No media is being played</div>
      <div class="artist" v-if="status && status.state !== 'stop' && track && track.artist" v-text="track.artist"></div>
      <div class="title" v-if="status && status.state !== 'stop' && track && track.title" v-text="track.title"></div>
    </div>

    <div class="time"  v-if="status && status.state === 'play'">
      <div class="row">
        <div class="progress-bar">
          <div class="elapsed" :style="{width: track.time ? 100*(status.elapsed/track.time) + '%' : '100%'}"></div>
          <div class="total"></div>
        </div>
      </div>

      <div class="row">
        <div class="col-6 time-elapsed" v-text="convertTime(status.elapsed)"></div>
        <div class="col-6 time-total" v-if="track.time" v-text="convertTime(track.time)"></div>
      </div>
    </div>

    <div class="controls" v-if="_withControls && status">
      <button @click="prev">
        <i class="fa fa-step-backward" />
      </button>
      <button class="play-pause" @click="playPause">
        <i class="fa fa-pause" v-if="status.state === 'play'" />
        <i class="fa fa-play" v-else />
      </button>
      <button @click="stop" v-if="status.state !== 'stop'">
        <i class="fa fa-stop" />
      </button>
      <button @click="next">
        <i class="fa fa-step-forward" />
      </button>
    </div>

    <div class="playback-status" v-if="status">
      <div class="status-property col-4">
        <i class="fa fa-volume-up"></i>&nbsp; <span v-text="status.volume + '%'"></span>
      </div>

      <div class="status-property col-2">
        <i class="fas fa-random" :class="{active: status.random}"></i>
      </div>
      <div class="status-property col-2">
        <i class="fas fa-redo" :class="{active: status.repeat}"></i>
      </div>
      <div class="status-property col-2">
        <i class="fa fa-bullseye" :class="{active: status.single}"></i>
      </div>
      <div class="status-property col-2">
        <i class="fa fa-utensils" :class="{active: status.consume}"></i>
      </div>
    </div>
  </div>
</template>

<script>
import Utils from "@/Utils";
import Loading from "@/components/Loading";

export default {
  name: "Music",
  components: {Loading},
  mixins: [Utils],
  props: {
    // Refresh interval in seconds.
    refreshSeconds: {
      type: Number,
      default: 60,
    },

    // Set to true if you also want to include music controls in the widget.
    withControls: {
      type: Boolean,
      default: true,
    }
  },

  data() {
    return {
      track: undefined,
      status: undefined,
      timer: undefined,
      loading: false,
      musicPlugin: 'music.mpd',

      syncTime: {
        timestamp: null,
        elapsed: null,
      },
    }
  },

  computed: {
    _withControls() {
      return this.parseBoolean(this.withControls)
    },
  },

  methods: {
    async refresh() {
      this.loading = true

      try {
        let status = await this.request(`${this.musicPlugin}.status`)
        let track = await this.request(`${this.musicPlugin}.current_track`)

        this._parseStatus(status)
        this._parseTrack(track)

        if (status.state === 'play' && !this.timer)
          this.startTimer()
        else if (status.state !== 'play' && this.timer)
          this.stopTimer()
      } finally {
        this.loading = false
      }
    },

    convertTime(time) {
      time = parseFloat(time)   // Normalize strings
      const t = {}
      t.h = parseInt(time/3600)
      t.m = parseInt(time/60 - t.h*60)
      t.s = parseInt(time - (t.h*3600 + t.m*60))

      for (const attr of ['m','s']) {
        t[attr] = '' + t[attr]
      }

      for (const attr of ['m','s']) {
        if (parseInt(t[attr]) < 10) {
          t[attr] = '0' + t[attr]
        }
      }

      const ret = []
      if (parseInt(t.h)) {
        ret.push(t.h)
      }

      ret.push(t.m, t.s)
      return ret.join(':')
    },

    async _parseStatus(status) {
      if (!status || status.length === 0)
        status = await this.request(`${this.musicPlugin}.status`)
      if (status?.pluginName)
        this.musicPlugin = status.pluginName
      if (!this.status)
        this.status = {}

      for (const [attr, value] of Object.entries(status)) {
        if (['consume','random','repeat','single','bitrate'].indexOf(attr) >= 0) {
          this.status[attr] = !!parseInt(value)
        } else if (['nextsong','nextsongid','playlist','playlistlength',
          'volume','xfade','song','songid'].indexOf(attr) >= 0) {
          this.status[attr] = parseInt(value)
        } else if (['elapsed'].indexOf(attr) >= 0) {
          this.status[attr] = parseFloat(value)
        } else {
          this.status[attr] = value
        }
      }
    },

    async _parseTrack(track) {
      if (!track || track.length === 0) {
        track = await this.request(`${this.musicPlugin}.current_track`)
      }

      if (!this.track)
        this.track = {}

      for (const [attr, value] of Object.entries(track)) {
        if (['id','pos','time','track','disc'].indexOf(attr) >= 0) {
          this.track[attr] = parseInt(value)
        } else {
          this.track[attr] = value
        }
      }
    },

    showNewTrackNotification() {
      this.notify({
        html: '<b>' + (this.track.artist || '[No Artist]') + '</b><br>' +
            (this.track.title || '[No Title]'),
        image: {
          icon: 'play',
        }
      })
    },

    async onNewPlayingTrack(event) {
      let previousTrack = undefined

      if (this.track) {
        previousTrack = {
          file: this.track.file,
          artist: this.track.artist,
          title: this.track.title,
        }
      }

      this.status.state = 'play'
      this.status.elapsed = 0
      this.track = {}
      this._parseTrack(event.track)

      let status = event.status ? event.status : await this.request(`${this.musicPlugin}.status`)
      this._parseStatus(status)
      this.startTimer()

      if (!previousTrack || (this.track.file !== previousTrack.file
          || this.track.artist !== previousTrack.artist
          || this.track.title !== previousTrack.title)) {
        this.showNewTrackNotification()
      }
    },

    onMusicStop(event) {
      this.status.state = 'stop'
      this.status.elapsed = 0
      this._parseStatus(event.status)
      this._parseTrack(event.track)
      this.stopTimer()
    },

    onMusicPlay(event) {
      this.status.state = 'play'
      this._parseStatus(event.status)
      this._parseTrack(event.track)
      this.startTimer()
    },

    onMusicPause(event) {
      this.status.state = 'pause'
      this._parseStatus(event.status)
      this._parseTrack(event.track)

      this.syncTime.timestamp = new Date()
      this.syncTime.elapsed = this.status.elapsed
    },

    onSeekChange(event) {
      if (event.position != null)
        this.status.elapsed = parseFloat(event.position)
      if (event.status)
        this._parseStatus(event.status)
      if (event.track)
        this._parseTrack(event.track)

      this.syncTime.timestamp = new Date()
      this.syncTime.elapsed = this.status.elapsed
    },

    onVolumeChange(event) {
      if (event.volume != null)
        this.status.volume = parseFloat(event.volume)
      if (event.status)
        this._parseStatus(event.status)
      if (event.track)
        this._parseTrack(event.track)
    },

    onRepeatChange(event) {
      this.status.repeat = event.state
    },

    onRandomChange(event) {
      this.status.random = event.state
    },

    onConsumeChange(event) {
      this.status.consume = event.state
    },

    onSingleChange(event) {
      this.status.single = event.state
    },

    startTimer() {
      if (this.timer != null) {
        this.stopTimer()
      }

      this.syncTime.timestamp = new Date()
      this.syncTime.elapsed = this.status.elapsed
      this.timer = setInterval(this.timerFunc, 1000)
    },

    stopTimer() {
      if (this.timer == null) {
        clearInterval(this.timer)
        this.timer = null
      }
    },

    timerFunc() {
      if (this.status.state !== 'play' || this.status.elapsed == null) {
        return
      }

      this.status.elapsed = this.syncTime.elapsed +
          ((new Date()).getTime()/1000) - (this.syncTime.timestamp.getTime()/1000)
    },

    async _run(action, args) {
      args = args || {}
      await this.request(`music.mpd.${action}`, args)
      await this.refresh()
    },

    async playPause() {
      return await this._run('pause')
    },

    async stop() {
      return await this._run('stop')
    },

    async prev() {
      return await this._run('previous')
    },

    async next() {
      return await this._run('next')
    },
  },

  mounted() {
    this.refresh()
    if (this.refreshSeconds) {
      setInterval(this.refresh, parseInt((this.refreshSeconds*1000).toFixed(0)))
    }

    this.subscribe(this.onNewPlayingTrack, 'widget-music-on-new-track', 'platypush.message.event.music.NewPlayingTrackEvent')
    this.subscribe(this.onMusicStop, 'widget-music-on-music-stop', 'platypush.message.event.music.MusicStopEvent')
    this.subscribe(this.onMusicPlay, 'widget-music-on-music-play', 'platypush.message.event.music.MusicPlayEvent')
    this.subscribe(this.onMusicPause, 'widget-music-on-music-pause', 'platypush.message.event.music.MusicPauseEvent')
    this.subscribe(this.onSeekChange, 'widget-music-on-music-seek', 'platypush.message.event.music.SeekChangeEvent')
    this.subscribe(this.onVolumeChange, 'widget-music-on-volume-change', 'platypush.message.event.music.VolumeChangeEvent')
    this.subscribe(this.onRepeatChange, 'widget-music-on-repeat-change', 'platypush.message.event.music.PlaybackRepeatModeChangeEvent')
    this.subscribe(this.onRandomChange, 'widget-music-on-random-change', 'platypush.message.event.music.PlaybackRandomModeChangeEvent')
    this.subscribe(this.onConsumeChange, 'widget-music-on-consume-change', 'platypush.message.event.music.PlaybackConsumeModeChangeEvent')
    this.subscribe(this.onSingleChange, 'widget-music-on-single-change', 'platypush.message.event.music.PlaybackSingleModeChangeEvent')
  },
}
</script>

<style lang="scss" scoped>
$progress-bar-bg: #ddd;
$playback-status-color: #757f70;

.music {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;

  .track {
    text-align: center;

    .unknown,
    .no-track {
      font-size: 2em;
    }

    .artist {
      font-size: 1.9em;
      font-weight: bold;
      margin-bottom: .25em;
    }

    .title {
      font-size: 1.8em;
      font-weight: normal;
    }
  }

  .time {
    width: 100%;
    margin-top: 1em;
    font-size: 1.2em;

    .row {
      padding: 0 .5em;
    }

    .time-total {
      text-align: right;
    }

    .progress-bar {
      width: 100%;
      height: 1em;
      position: relative;
      margin-bottom: .75em;

      .total {
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        background: $progress-bar-bg;
        border-radius: 0.5em;
      }

      .elapsed {
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        background: $selected-bg;
        border-radius: 0.5em;
        z-index: 1;
      }
    }
  }

  .playback-status {
    position: absolute;
    bottom: 0;
    border-top: $default-border-2;
    color: $playback-status-color;
    width: 100%;
    height: 2em;

    .status-property {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
    }

    .active {
      color: $default-hover-fg;
    }
  }

  .controls {
    margin-top: .5em;
    font-size: 1.2em;

    button {
      background: none;
      border: none;

      &:hover {
        color: $default-hover-fg;
      }

      &.play-pause {
        color: $selected-fg;
        font-size: 1.5em;
      }
    }
  }
}
</style>

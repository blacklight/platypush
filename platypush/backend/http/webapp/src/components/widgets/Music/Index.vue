<template>
  <Loading v-if="loading" />
  <div class="music" v-else>
    <div class="background" v-if="image">
      <div class="image" :style="{backgroundImage: 'url(' + image + ')'}" />
    </div>

    <div class="foreground">
      <div class="top">
        <div class="section" :class="{'has-image': !!image, 'has-progress': status?.state === 'play'}">
          <div class="track">
            <div class="unknown" v-if="!status">[Unknown state]</div>
            <div class="no-track" v-if="status && status.state === 'stop'">No media is being played</div>
            <div class="artist" v-if="status && status.state !== 'stop' && track && track.artist" v-text="track.artist"></div>
            <div class="title" v-if="status && status.state !== 'stop' && track && track.title" v-text="track.title"></div>
          </div>

          <div class="progress-bar" v-if="status?.state === 'play'">
            <div class="row">
              <ProgressBar
                :duration="track.time"
                :elapsed="status.elapsed"
                :status="status"
                @seek="seek" />
            </div>
          </div>

          <div class="controls" v-if="_withControls && status">
            <button title="Previous" @click="prev">
              <i class="fa fa-step-backward" />
            </button>
            <button class="play-pause" @click="playPause"
                :title="status.state === 'play' ? 'Pause' : 'Play'">
              <i class="fa fa-pause" v-if="status.state === 'play'" />
              <i class="fa fa-play" v-else />
            </button>
            <button title="Stop" @click="stop" v-if="status.state !== 'stop'">
              <i class="fa fa-stop" />
            </button>
            <button title="Next" @click="next">
              <i class="fa fa-step-forward" />
            </button>
          </div>
        </div>
      </div>

      <div class="bottom">
        <div class="playback-status section" :class="{'has-image': !!image}" v-if="status">
          <div class="status-property col-4 volume fade-in" v-if="!showVolumeBar">
            <button title="Volume" @click="showVolumeBar = true">
              <i class="fa fa-volume-up" />
              &nbsp; {{ status.volume }}%
            </button>
          </div>

          <div class="status-property col-4 volume fade-in" v-else>
            <div class="row">
              <i class="fa fa-volume-up" /> &nbsp;
              <Slider :range="[0, 100]" :value="status.volume" @change="setVolume" />
            </div>
          </div>

          <div class="status-property col-2">
            <button title="Random" @click="random">
              <i class="fas fa-random" :class="{active: status.random}"></i>
            </button>
          </div>
          <div class="status-property col-2">
            <button title="Repeat" @click="repeat">
              <i class="fas fa-redo" :class="{active: status.repeat}"></i>
            </button>
          </div>
          <div class="status-property col-2">
            <button title="Single" @click="single">
              <i class="fa fa-bullseye" :class="{active: status.single}"></i>
            </button>
          </div>
          <div class="status-property col-2">
            <button title="Consume" @click="consume">
              <i class="fa fa-utensils" :class="{active: status.consume}"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Utils from "@/Utils";
import Loading from "@/components/Loading";
import Status from "@/mixins/Music/Status";
import ProgressBar from "@/components/Media/ProgressBar";
import Slider from "@/components/elements/Slider";

export default {
  name: "Music",
  components: {Loading, ProgressBar, Slider},
  mixins: [Status, Utils],
  props: {
    // Music plugin to use (default: music.mopidy).
    plugin: {
      type: String,
      default: 'music.mopidy',
    },

    // Refresh interval in seconds.
    refreshSeconds: {
      type: Number,
      default: 60,
    },

    // Set to true if you also want to include music controls in the widget.
    withControls: {
      type: Boolean,
      default: true,
    },
  },

  data() {
    return {
      track: null,
      status: {},
      timer: null,
      loading: false,
      showVolumeBar: false,
      images: {},
      maxImages: 100,

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
    
    _refreshSeconds() {
      return parseFloat(this.refreshSeconds)
    },

    trackUri() {
      return this.track?.uri || this.track?.file
    },

    image() {
      if (this.status?.state === 'stop')
        return null

      return this.images[this.trackUri] || this.track?.image || this.status?.image
    },
  },

  methods: {
    async refresh() {
      this.loading = true

      try {
        let status = await this.request(`${this.plugin}.status`) || {}
        let track = await this.request(`${this.plugin}.current_track`)

        this._parseStatus(status)
        this._parseTrack(track)

        if (status.state === 'play' && !this.timer)
          this.startTimer()
        else if (status.state !== 'play' && this.timer)
          this.stopTimer()

        if (status.state !== 'stop' && !this.image)
          await this.refreshImage()
      } finally {
        this.loading = false
      }
    },

    async refreshImage() {
      if (!this.trackUri)
        return

      if (!this.images[this.trackUri]) {
         const trackImage = (
          await this.request(`${this.plugin}.get_images`, {resources: [this.trackUri]})
        )[this.trackUri]

        if (Object.keys(this.images).length > this.maxImages) {
          delete this.images[Object.keys(this.images)[0]]
        }

        this.images[this.trackUri] = trackImage
      }

      return this.images[this.trackUri]
    },

    async _parseStatus(status) {
      const statusPlugin = status.pluginName
      if (statusPlugin && this.plugin && statusPlugin !== this.plugin)
        return  // Ignore status updates from other plugins

      if (!status || Object.keys(status).length === 0)
        status = await this.request(`${this.plugin}.status`) || {}
      if (!this.status)
        this.status = {}

      this.status = this.parseStatus(status)
    },

    async _parseTrack(track) {
      if (!track || track.length === 0) {
        track = await this.request(`${this.plugin}.current_track`)
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

    async seek(position) {
      await this.request(`${this.plugin}.seek`, {position: position})
    },

    async setVolume(event) {
      await this.request(`${this.plugin}.set_volume`, {volume: event.target.value})
      this.showVolumeBar = false
    },

    async random() {
      await this.request(`${this.plugin}.random`)
    },

    async repeat() {
      await this.request(`${this.plugin}.repeat`)
    },

    async consume() {
      await this.request(`${this.plugin}.consume`)
    },

    async single() {
      await this.request(`${this.plugin}.single`)
    },

    async onNewPlayingTrack(event) {
      let previousTrack = null

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

      let status = event.status ? event.status : await this.request(`${this.plugin}.status`)
      this._parseStatus(status)
      this.startTimer()

      if (!previousTrack || (this.track.file !== previousTrack.file
          || this.track.artist !== previousTrack.artist
          || this.track.title !== previousTrack.title)) {
        this.showNewTrackNotification()
      }

      if (!this.image)
        await this.refreshImage()
    },

    onMusicStop(event) {
      this.status.state = 'stop'
      this.status.elapsed = 0
      this._parseStatus(event.status)
      this._parseTrack(event.track)
      this.stopTimer()
    },

    async onMusicPlay(event) {
      this.status.state = 'play'
      this._parseStatus(event.status)
      this._parseTrack(event.track)
      this.startTimer()

      if (!this.image)
        await this.refreshImage()
    },

    async onMusicPause(event) {
      this.status.state = 'pause'
      this._parseStatus(event.status)
      this._parseTrack(event.track)

      this.syncTime.timestamp = new Date()
      this.syncTime.elapsed = this.status.elapsed

      if (!this.image)
        await this.refreshImage()
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
    if (this._refreshSeconds) {
      setInterval(this.refresh, this._refreshSeconds * 1000)
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
$playback-status-color: #757f70;
$bottom-height: 2em;

.music {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;

  .background {
    width: 100%;
    height: 100%;
    position: absolute;

    .image {
      width: 100%;
      height: 100%;
      background-size: cover;
      background-position: center;
      filter: contrast(0.15) opacity(0.5);
    }
  }

  @mixin top {
    width: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: relative;
  }

  .foreground {
    @include top;
    height: 100%;
  }

  .top {
    @include top;
    height: calc(100% - #{$bottom-height});

    .section {
      flex-direction: column;

      &.has-image {
        padding: 1em;
        border-radius: 1em;
      }

      &.has-progress {
        width: calc(100% - 0.5em);
        padding: 1.5em 0.25em;
      }
    }
  }

  .bottom {
    width: 100%;
    height: $bottom-height;

    .section {
      border-top: $default-border-2;

      &.has-image {
        border-top: none;
        box-shadow: 0 0 0.25em rgba(0, 0, 0, 0.15);
      }
    }
  }

  .section {
    display: flex;
    align-items: center;
    justify-content: center;

    &.has-image {
      background: rgba(255, 255, 255, 0.4);
      box-shadow: 0 0 0.25em rgba(0, 0, 0, 0.15);
    }
  }

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

  .progress-bar {
    width: 100%;
    height: 1em;
    font-size: 1.2em;
    position: relative;
    margin-top: 1.5em;
    margin-bottom: .75em;
    padding: 0 .5em;
  }

  .playback-status {
    color: $playback-status-color;

    .status-property {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
    }

    .active {
      color: $default-hover-fg;

      &:hover {
        color: $playback-status-color !important;
      }
    }

    button {
      color: $playback-status-color;
      padding: 0.25em 0.5em;
      border-top: 1px solid transparent;

      &:hover {
        border-top: 1px solid $default-hover-fg;
      }
    }
  }

  .controls {
    display: flex;
    margin-top: .5em;
    font-size: 1.2em;
  }

  button {
    background: none;
    border: none;
    cursor: pointer;

    &:hover {
      color: $default-hover-fg !important;
    }

    &.play-pause {
      color: $selected-fg !important;
      font-size: 1.5em;
    }
  }

  .volume {
    .row {
      width: calc(100% - 1em);
      margin: 0 .5em;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
}
</style>

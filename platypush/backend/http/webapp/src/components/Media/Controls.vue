<template>
  <div class="extension fade-in" :class="{hidden: !expanded}">
    <div class="image-container"
         @click.prevent="searchAlbum"
         v-if="status?.state !== 'stop'">
      <div class="remote-image-container" v-if="trackImage">
        <img class="image" :src="trackImage" :alt="trackTitle">
      </div>

      <div class="icon-container" v-else>
        <i class="icon fas fa-compact-disc"
          :class="{playing: status?.state === 'play'}" />
      </div>
    </div>

    <div class="row buttons-container">
      <div class="buttons">
        <div class="buttons">
          <button @click="$emit('previous')" title="Play previous track" v-if="buttons_.previous">
            <i class="icon fa fa-step-backward"></i>
          </button>
          <button @click="$emit('stop')" v-if="buttons_.stop && status.state !== 'stop'" title="Stop playback">
            <i class="icon fa fa-stop"></i>
          </button>
          <button @click="$emit('next')" title="Play next track" v-if="buttons_.next">
            <i class="icon fa fa-step-forward"></i>
          </button>
        </div>
      </div>
    </div>

    <div class="row">
      <VolumeSlider
          :range="volumeRange"
          :status="status"
          :value="status.volume"
          @mute="$emit('mute')"
          @set-volume="$emit('set-volume', $event)"
          @unmute="$emit('unmute')" />

      <ExtraControls
          :buttons="buttons_"
          :status="status"
          @consume="$emit('consume', !status.consume)"
          @random="$emit('random', !status.random)"
          @repeat="$emit('repeat', !status.repeat)" />
    </div>

    <div class="row">
      <ProgressBar :elapsed="elapsed" :duration="duration" :status="status" @seek="$emit('seek', $event)" />
    </div>
  </div>

  <div class="controls">
    <div class="playback-controls until tablet col-2">
      <PlayPauseButton :status="status" @play="$emit('play')" @pause="$emit('pause')" />
    </div>

    <div class="track-container col-s-9 col-m-9 col-l-3">
      <div class="track-info" @click="$emit('info', track)" v-if="track && status?.state !== 'stop'">
        <div class="img-container" v-if="trackImage">
          <img class="image from desktop" :src="trackImage" :alt="trackTitle">
        </div>

        <div class="title-container">
          <div class="title" v-if="status.state === 'play' || status.state === 'pause'">
            <a :href="$route.fullPath" v-text="trackTitle"
               @click.prevent="searchAlbum" v-if="track.album"></a>
            <a v-text="trackTitle" v-else-if="track.url"></a>
            <span v-text="trackTitle" v-else></span>
          </div>
          <div class="artist" v-if="trackArtistName?.length && (status.state === 'play' || status.state === 'pause')">
            <a v-text="trackArtistName" @click.prevent="searchArtist"></a>
          </div>
        </div>
      </div>
    </div>

    <div class="playback-controls from desktop col-6">
      <div class="row buttons">
        <button @click="$emit('previous')" title="Play previous track" v-if="buttons_.previous">
          <i class="icon fa fa-step-backward"></i>
        </button>
        <PlayPauseButton :status="status" @play="$emit('play')" @pause="$emit('pause')" />
        <button @click="$emit('stop')" v-if="buttons_.stop && status.state !== 'stop'" title="Stop playback">
          <i class="icon fa fa-stop"></i>
        </button>
        <button @click="$emit('next')" title="Play next track" v-if="buttons_.next">
          <i class="icon fa fa-step-forward"></i>
        </button>
      </div>

      <div class="row">
        <ProgressBar :elapsed="elapsed" :duration="duration" :status="status" @seek="$emit('seek', $event)" />
      </div>
    </div>

    <div class="col-1 until tablet right-controls">
      <button @click="expanded = !expanded" :title="expanded ? 'Show more controls' : 'Hide extra controls'">
        <i class="fas" :class="[`fa-chevron-${expanded ? 'down' : 'up'}`]" />
      </button>
    </div>

    <div class="col-3 from desktop right-controls">
      <VolumeSlider :value="status.volume" :range="volumeRange" :status="status"
        @mute="$emit('mute')" @unmute="$emit('unmute')"
        @set-volume="$emit('set-volume', $event)" />

      <ExtraControls :status="status" :buttons="buttons_"
          @consume="$emit('consume', !status.consume)"
          @random="$emit('random', !status.random)"
          @repeat="$emit('repeat', !status.repeat)" />
    </div>
  </div>
</template>

<script>
import Utils from "@/Utils"
import MediaUtils from "@/components/Media/Utils";
import ExtraControls from "./ExtraControls";
import PlayPauseButton from "./PlayPauseButton";
import ProgressBar from "./ProgressBar";
import VolumeSlider from "./VolumeSlider";

export default {
  components: {ExtraControls, PlayPauseButton, ProgressBar, VolumeSlider},
  mixins: [Utils, MediaUtils],
  emits: [
    'consume',
    'info',
    'mute',
    'next',
    'pause',
    'play',
    'previous',
    'random',
    'repeat',
    'search',
    'seek',
    'set-volume',
    'stop',
    'unmute',
  ],

  props: {
    track: {
      type: Object,
    },

    status: {
      type: Object,
      default: () => {},
    },

    image: {
      type: String,
      default: null,
    },

    // Enabled playback buttons
    buttons: {
      type: Object,
      default: () => {
        return {
          previous: true,
          next: true,
          stop: true,
          consume: true,
          random: true,
          repeat: true,
        }
      },
    },

    // Volume range
    volumeRange: {
      type: Array,
      default: () => [0, 100],
    }
  },

  data() {
    const buttons = Object.keys(this.buttons)?.length ? this.buttons : {
      previous: true,
      next: true,
      stop: true,
      consume: true,
      random: true,
      repeat: true,
    }

    return {
      expanded: false,
      lastSync: 0,
      elapsed: this.status?.elapsed || this.status?.position,
      buttons_: buttons,
    }
  },

  computed: {
    duration() {
      const duration = this.status?.duration != null ? this.status.duration : this.track?.duration
      if (duration != null)
        return parseFloat(duration)

      return null
    },

    trackArtistId() {
      return typeof this.track?.artist === 'object' ? this.track.artist.id : null
    },

    trackArtistName() {
      if (typeof this.track?.artist === 'string')
        return this.track.artist

      return this.track?.artist?.name || this.track?.artist?.title
    },

    trackImage() {
      if (this.track?.images?.length)
        return this.track.images[0].url

      return this.track?.image || this.image
    },

    trackTitle() {
      return this.track?.title || this.track?.name || '[No Title]'
    },
  },

  methods: {
    getTime() {
      return (new Date()).getTime() / 1000
    },

    searchAlbum() {
      if (!(this.track?.artist && this.track?.album))
        return

      const args = {
        artist: this.track.artist,
        album: this.track.album,
      }

      if (this.track.album_uri)
        args.uris = [this.track.album_uri]

      this.$emit('search', args)
    },

    searchArtist() {
      if (!this.trackArtistName?.length)
        return

      const args = {
        artist: this.trackArtistName,
      }

      if (this.track.artist_uri)
        args.uris = [this.track.album_uri]

      this.$emit('search', args)
    },
  },

  mounted() {
    const self = this
    this.lastSync = this.getTime()

    this.$watch(() => this.track, (track) => {
      if (!track || self.status?.state !== 'play')
        self.lastSync = this.getTime()
    })

    this.$watch(() => this.status, () => {
      self.lastSync = this.getTime()
    })

    setInterval(() => {
      if (self.status?.state !== 'stop') {
        self.elapsed = (self.status?.elapsed || self.status?.position || 0)
        if (self.status?.state === 'play')
          self.elapsed += Math.round(this.getTime() - self.lastSync)
      }
    }, 1000)
  },
}
</script>

<style lang="scss" scoped>
@import 'vars.scss';

button {
  border: 0;
  background: none;

  &:hover {
    border: 0;

    .icon {
      color: $default-hover-fg;
    }
  }

  &.enabled {
    color: $selected-fg;
  }
}

.extension {
  background: $media-ctrl-ext-bg;
  box-shadow: $media-ctrl-ext-shadow;
  border-radius: 1em 1em 0 0;
  flex-direction: column;
  display: none;
  overflow: hidden;
  padding: .5em;

  @include until($desktop) {
    display: flex;
  }

  :deep(.extra-controls-container) {
    @extend .pull-right;
    flex: 1;
  }

  :deep(.progress-bar-container, .volume-slider-container) {
    font-size: 1.25em;
  }

  :deep(.volume-slider-container) {
    margin: 1em 0;
  }

  .row {
    display: flex;
  }

  .buttons-container {
    width: calc(100% + 1em);
    margin-left: -0.5em;
    font-size: 2em;
    justify-content: center;
    box-shadow: $border-shadow-bottom;

    button {
      text-align: center;

      &:hover {
        color: $default-hover-fg;
      }

      i {
        margin: auto;
      }
    }
  }

  .buttons {
    display: flex;
    justify-content: center;
    margin: 0;
  }

  .image-container {
    width: 100%;
    display: flex;
    justify-content: center;
    cursor: pointer;

    .remote-image-container {
      height: 30vh;

      .image {
        height: 100%;
      }
    }

    .icon-container {
      padding: 0.05em;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 15em;
      opacity: 0.5;
      border: $default-border-2;
      box-shadow: $border-shadow-bottom;

      &:hover {
        color: $default-hover-fg;
        opacity: 1;
      }
    }

    .icon {
      &.playing {
        animation-duration: 3s;
        animation-name: rotate;
        animation-iteration-count: infinite;
      }
    }

    @keyframes rotate {
       0% {
         transform: rotate(0deg);
         opacity: 1;
       }

       50% {
         opacity: 0.5;
       }

       100% {
         transform: rotate(359deg);
         opacity: 1;
       }
    }
  }
}

.controls {
  width: 100%;
  height: $media-ctrl-panel-height;
  display: flex;
  padding: 1em .5em;
  overflow: hidden;
  align-items: center;

  button {
    background: none !important;
  }

  .row {
    width: 100%;
    display: flex;
  }

  .track-container {
    height: 100%;
    display: flex;
    align-items: center;
    margin-left: 0;

    @include until($desktop) {
      flex-direction: column;
      text-align: center;
    }

    a {
      color: initial;
      text-decoration: none;

      &:hover {
        color: $default-hover-fg;
      }
    }

    .artist, .title {
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .artist {
      opacity: 0.6;
      letter-spacing: .04em;
    }

    .title {
      font-weight: normal;
      font-size: 1em;
      letter-spacing: .05em;
      margin-bottom: .25em;
    }

    .image {
      width: 5em;
      max-height: 100%;
      display: inline-flex;
    }
  }

  .track-info {
    height: 100%;
    display: flex;

    @include until($desktop) {
      flex-direction: column;
    }

    @include from($desktop) {
      flex-direction: row;
      align-items: center;

      .img-container {
        max-width: 100%;
        max-height: calc(100% + 3em);
      }

      .image {
        padding: 0.5em;
        max-height: 100%;
      }
    }
  }

  .playback-controls {
    .row {
      justify-content: center;
    }

    .buttons {
      margin-bottom: .5em;
      align-items: center;
    }

    button {
      padding: 0.5em;
      margin: 0 .75em;

      .play-pause {
        color: $play-btn-fg;
        font-size: 1.75em;

        &:hover {
          color: $default-hover-fg-2;
        }
      }
    }
  }

  .right-controls {
    @extend .pull-right;

    display: flex;
    flex-direction: column;
    flex: 1;
    align-items: flex-end;

    button {
      padding: 0.5em;
    }

    :deep(.extra-controls-container) {
      @extend .pull-right;
    }
  }

  .seek-slider {
    width: 75%;
  }
}
</style>

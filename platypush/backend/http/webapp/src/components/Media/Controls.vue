<template>
  <div class="extension fade-in" :class="{hidden: !expanded}">
    <div class="row">
      <div class="col-3">
      </div>
      <div class="col-6">
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
      <div class="col-3">
      </div>
    </div>

    <div class="row">
      <div class="col-9 volume-container">
        <VolumeSlider :value="status.volume" :range="volumeRange" :status="status"
          @mute="$emit('mute')" @unmute="$emit('unmute')"
          @set-volume="$emit('set-volume', $event)" />
      </div>

      <div class="col-3 list-controls">
        <button @click="$emit('consume', !status.consume)" :class="{enabled: status.consume}"
                title="Toggle consume mode" v-if="buttons_.consume">
          <i class="icon fa fa-utensils"></i>
        </button>

        <button @click="$emit('random', !status.random)" :class="{enabled: status.random}"
                title="Toggle shuffle" v-if="buttons_.random">
          <i class="icon fa fa-random"></i>
        </button>

        <button @click="$emit('repeat', !status.repeat)" :class="{enabled: status.repeat}"
                title="Toggle repeat" v-if="buttons_.repeat">
          <i class="icon fa fa-redo"></i>
        </button>
      </div>
    </div>

    <div class="row">
      <div class="col-s-2 col-m-1 time">
          <span class="elapsed-time"
                v-text="elapsed != null && (status.state === 'play' || status.state === 'pause') ? convertTime(elapsed) : '-:--'"></span>
      </div>
      <div class="col-s-8 col-m-10 time-bar">
        <Slider :value="elapsed" :range="[0, duration]" :disabled="!duration || status.state === 'stop'"
                @mouseup="$emit('seek', $event.target.value)" />
      </div>
      <div class="col-s-2 col-m-1 time">
          <span class="total-time"
                v-text="duration && status.state !== 'stop' ? convertTime(duration) : '-:--'"></span>
      </div>
    </div>
  </div>

  <div class="controls">
    <div class="playback-controls until tablet col-2">
      <button @click="$emit(status.state === 'play' ? 'pause' : 'play')"
              :title="status.state === 'play' ? 'Pause' : 'Play'">
        <i class="icon play-pause fa fa-pause" v-if="status.state === 'play'"></i>
        <i class="icon play-pause fa fa-play" v-else></i>
      </button>
    </div>

    <div class="track-container col-s-8 col-m-8 col-l-3">
      <div class="track-info" v-if="track && status?.state !== 'stop'">
        <div class="title" v-if="status.state === 'play' || status.state === 'pause'">
          <a :href="$route.fullPath" v-text="track.title?.length ? track.title : '[No Title]'"
             @click.prevent="$emit('search', {artist: track.artist, album: track.album})" v-if="track.album"></a>
          <a :href="track.url" v-text="track.title?.length ? track.title : '[No Title]'" v-else-if="track.url"></a>
          <span v-text="track.title?.length ? track.title : '[No Title]' " v-else></span>
        </div>
        <div class="artist" v-if="track.artist?.length && (status.state === 'play' || status.state === 'pause')">
          <a :href="$route.fullPath" v-text="track.artist" @click.prevent="$emit('search', {artist: track.artist})"></a>
        </div>
      </div>
    </div>

    <div class="playback-controls from desktop col-6">
      <div class="row buttons">
        <button @click="$emit('previous')" title="Play previous track" v-if="buttons_.previous">
          <i class="icon fa fa-step-backward"></i>
        </button>
        <button @click="$emit(status.state === 'play' ? 'pause' : 'play')"
                :title="status.state === 'play' ? 'Pause' : 'Play'">
          <i class="icon play-pause fa fa-pause" v-if="status.state === 'play'"></i>
          <i class="icon play-pause fa fa-play" v-else></i>
        </button>
        <button @click="$emit('stop')" v-if="buttons_.stop && status.state !== 'stop'" title="Stop playback">
          <i class="icon fa fa-stop"></i>
        </button>
        <button @click="$emit('next')" title="Play next track" v-if="buttons_.next">
          <i class="icon fa fa-step-forward"></i>
        </button>
      </div>

      <div class="row">
        <div class="col-1 time">
          <span class="elapsed-time"
                v-text="elapsed != null && (status.state === 'play' || status.state === 'pause') ? convertTime(elapsed) : '-:--'"></span>
        </div>
        <div class="col-10">
          <Slider :value="elapsed" :range="[0, duration]" :disabled="!duration || status.state === 'stop'"
                  @mouseup="$emit('seek', $event.target.value)" />
        </div>
        <div class="col-1 time">
          <span class="total-time"
                v-text="duration && status.state !== 'stop' ? convertTime(duration) : '-:--'"></span>
        </div>
      </div>
    </div>

    <div class="col-2 pull-right until tablet right-buttons">
      <button @click="expanded = !expanded" :title="expanded ? 'Show more controls' : 'Hide extra controls'">
        <i class="fas" :class="[`fa-chevron-${expanded ? 'down' : 'up'}`]" />
      </button>
    </div>

    <div class="col-3 pull-right from desktop">
      <div class="row volume-container">
        <VolumeSlider :value="status.volume" :range="volumeRange" :status="status"
          @mute="$emit('mute')" @unmute="$emit('unmute')"
          @set-volume="$emit('set-volume', $event)" />
      </div>
      <div class="row list-controls">
        <button @click="$emit('consume')" :class="{enabled: status.consume}" title="Toggle consume mode" v-if="buttons_.consume">
          <i class="icon fa fa-utensils"></i>
        </button>
        <button @click="$emit('random')" :class="{enabled: status.random}" title="Toggle shuffle" v-if="buttons_.random">
          <i class="icon fa fa-random"></i>
        </button>
        <button @click="$emit('repeat')" :class="{enabled: status.repeat}" title="Toggle repeat" v-if="buttons_.repeat">
          <i class="icon fa fa-redo"></i>
        </button>
      </div>

    </div>
  </div>
</template>

<script>
import Utils from "@/Utils"
import MediaUtils from "@/components/Media/Utils";
import Slider from "@/components/elements/Slider";
import VolumeSlider from "./VolumeSlider";

export default {
  components: {Slider, VolumeSlider},
  mixins: [Utils, MediaUtils],
  emits: [
    'consume',
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
      return this.status?.duration != null ? this.status.duration : this.track?.duration
    },
  },

  methods: {
    getTime() {
      return (new Date()).getTime() / 1000
    }
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
  box-shadow: $border-shadow-bottom;
  flex-direction: column;
  display: none;
  overflow: hidden;

  @include until($desktop) {
    display: flex;
    padding-top: .5em;
  }

  .row {
    display: flex;
  }

  .buttons {
    justify-content: center;
    margin: 0;
  }

  .volume-container,
  .list-controls {
    display: flex;
    align-items: center;

    button {
      padding: 0 .25em;
    }
  }

  .list-controls {
    margin-top: -.5em;
    flex-flow: row-reverse;
  }

  .time {
    &:first-child {
      margin-left: .25em;
    }

    &:last-child {
      margin-right: .25em;
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

  .row {
    width: 100%;
    display: flex;
  }

  .volume-container {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .track-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    margin-left: 0;

    @include until($tablet) {
      align-items: center;
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
  }

  .playback-controls {
    &.mobile {
      display: none;

      @include until($tablet) {
        display: flex !important;
        align-items: center;
      }
    }

    &.tablet {
      display: none;

      @media screen and (min-width: $tablet) and (max-width: $desktop - 1) {
        display: flex !important;
        align-items: center;
      }
    }

    .row {
      justify-content: center;
    }

    .buttons {
      height: 50%;
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

  .list-controls {
    height: 50%;
    opacity: 0.7;
    display: flex;
    align-items: center;
    margin-bottom: 1em;
    flex-flow: row-reverse;
  }

  .mobile.right-buttons {
    @include until ($desktop) {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      flex: 1;
    }
  }

  .pull-right {
    button {
      padding: 0.5em;
    }
  }

  .seek-slider {
    width: 75%;
  }
}

.time {
  font-size: .7em;
  position: relative;
}

.elapsed-time {
  text-align: right;
  float: right;
}

.time-bar {
  flex-grow: 1;
  margin: 0 .5em;
}
</style>

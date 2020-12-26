<template>
  <div class="extension fade-in" :class="{hidden: !expanded}">
    <div class="row">
      <div class="col-3">
      </div>
      <div class="col-6">
        <div class="buttons">
          <button @click="$emit('previous')" title="Play previous track" v-if="buttons.previous">
            <i class="icon fa fa-step-backward"></i>
          </button>
          <button @click="$emit('stop')" v-if="buttons.stop && status.state !== 'stop'" title="Stop playback">
            <i class="icon fa fa-stop"></i>
          </button>
          <button @click="$emit('next')" title="Play next track" v-if="buttons.next">
            <i class="icon fa fa-step-forward"></i>
          </button>
        </div>
      </div>
      <div class="col-3">
      </div>
    </div>

    <div class="row">
      <div class="col-9 volume-container">
        <div class="col-1">
          <button :disabled="status.muted == null" @click="$emit(status.muted ? 'unmute' : 'mute')">
            <i class="icon fa fa-volume-up"></i>
          </button>
        </div>
        <div class="col-11 volume-slider">
          <Slider :value="status.volume" :range="volumeRange" :disabled="status.volume == null"
                  @mouseup="$emit('set-volume', $event.target.value)" />
        </div>
      </div>

      <div class="col-3 list-controls">
        <button @click="$emit('consume', !status.consume)" :class="{enabled: status.consume}"
                title="Toggle consume mode" v-if="buttons.consume">
          <i class="icon fa fa-utensils"></i>
        </button>

        <button @click="$emit('random', !status.random)" :class="{enabled: status.random}"
                title="Toggle shuffle" v-if="buttons.random">
          <i class="icon fa fa-random"></i>
        </button>

        <button @click="$emit('repeat', !status.repeat)" :class="{enabled: status.repeat}"
                title="Toggle repeat" v-if="buttons.repeat">
          <i class="icon fa fa-redo"></i>
        </button>
      </div>
    </div>

    <div class="row">
      <div class="col-s-2 col-m-1 time">
          <span class="elapsed-time"
                v-text="elapsed != null && status.state !== 'stop' ? convertTime(elapsed) : '-:--'"></span>
      </div>
      <div class="col-s-8 col-m-10">
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
    <div class="playback-controls mobile tablet col-2">
      <button @click="$emit(status.state === 'play' ? 'pause' : 'play')"
              :title="status.state === 'play' ? 'Pause' : 'Play'">
        <i class="icon play-pause fa fa-pause" v-if="status.state === 'play'"></i>
        <i class="icon play-pause fa fa-play" v-else></i>
      </button>
    </div>

    <div class="track-container col-s-8 col-m-8 col-l-3">
      <div class="track-info" v-if="track && status?.state !== 'stop'">
        <div class="title">
          <a href="#" v-text="track.title" @click="$emit('search', {album: track.album})" v-if="track.album"></a>
          <span v-text="track.title" v-else></span>
        </div>
        <div class="artist" v-if="track.artist">
          <a href="#" v-text="track.artist" @click="$emit('search', {artist: track.artist})"></a>
        </div>
      </div>
    </div>

    <div class="playback-controls desktop col-6">
      <div class="row buttons">
        <button @click="$emit('previous')" title="Play previous track" v-if="buttons.previous">
          <i class="icon fa fa-step-backward"></i>
        </button>
        <button @click="$emit(status.state === 'play' ? 'pause' : 'play')"
                :title="status.state === 'play' ? 'Pause' : 'Play'">
          <i class="icon play-pause fa fa-pause" v-if="status.state === 'play'"></i>
          <i class="icon play-pause fa fa-play" v-else></i>
        </button>
        <button @click="$emit('stop')" v-if="buttons.stop && status.state !== 'stop'" title="Stop playback">
          <i class="icon fa fa-stop"></i>
        </button>
        <button @click="$emit('next')" title="Play next track" v-if="buttons.next">
          <i class="icon fa fa-step-forward"></i>
        </button>
      </div>

      <div class="row">
        <div class="col-1 time">
          <span class="elapsed-time"
                v-text="elapsed != null && status.state !== 'stop' ? convertTime(elapsed) : '-:--'"></span>
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

    <div class="col-2 pull-right mobile tablet right-buttons">
      <button @click="expanded = !expanded" :title="expanded ? 'Show more controls' : 'Hide extra controls'">
        <i class="fas" :class="[`fa-chevron-${expanded ? 'down' : 'up'}`]" />
      </button>
    </div>

    <div class="col-3 pull-right desktop">
      <div class="row list-controls">
        <button @click="$emit('consume')" :class="{enabled: status.consume}" title="Toggle consume mode" v-if="buttons.consume">
          <i class="icon fa fa-utensils"></i>
        </button>
        <button @click="$emit('random')" :class="{enabled: status.random}" title="Toggle shuffle" v-if="buttons.random">
          <i class="icon fa fa-random"></i>
        </button>
        <button @click="$emit('repeat')" :class="{enabled: status.repeat}" title="Toggle repeat" v-if="buttons.repeat">
          <i class="icon fa fa-redo"></i>
        </button>
      </div>

      <div class="row volume-container">
        <div class="col-2">
          <button :disabled="status.muted == null" @click="$emit(status.muted ? 'unmute' : 'mute')">
            <i class="icon fa fa-volume-up"></i>
          </button>
        </div>
        <div class="col-10">
          <Slider :value="status.volume" :range="volumeRange" :disabled="status.volume == null"
                  @mouseup="$emit('set-volume', $event.target.value)" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Utils from "@/Utils"
import MediaUtils from "@/components/Media/Utils";
import Slider from "@/components/elements/Slider";

export default {
  name: "Controls",
  components: {Slider},
  mixins: [Utils, MediaUtils],
  emits: ['search', 'previous', 'next', 'play', 'pause', 'stop', 'seek', 'consume', 'random', 'repeat',
    'set-volume', 'mute', 'unmute'],

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
    return {
      expanded: false,
      lastSync: 0,
      elapsed: this.status?.elapsed,
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

    this.$watch(() => self.track, (track) => {
      if (!track || self.status?.state !== 'play')
        self.lastSync = this.getTime()
    })

    this.$watch(() => self.status, () => {
      self.lastSync = this.getTime()
    })

    setInterval(() => {
      if (self.status?.state === 'play')
        self.elapsed = (self.status?.elapsed || 0) + Math.round(this.getTime() - self.lastSync)
    }, 1000)
  },
}
</script>

<style lang="scss" scoped>
@import 'vars.scss';

button {
  border: 0;
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

  .volume-slider {
    margin-left: 2.25em;
  }
}

.controls {
  width: 100%;
  height: $media-ctrl-panel-height;
  display: flex;
  padding: 1em .5em;
  overflow: hidden;

  .row {
    width: 100%;
    display: flex;
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
      align-items: center;
    }

    button {
      padding: 0;
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
      justify-content: right;
    }
  }

  .pull-right {
    button {
      padding: 0;
    }

    .volume-container {
      button {
        background: none;
      }
    }
  }

  .seek-slider {
    width: 75%;
  }

  .volume-slider {
    width: 75%;
    margin-right: 1rem;
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

.mobile {
  @include from($tablet) {
    display: none;
  }
}

.tablet {
  @media screen and (max-width: $tablet), screen and (min-width: $desktop - 1) {
    display: none;
  }
}

.desktop {
  @include until($desktop) {
    display: none;
  }
}
</style>

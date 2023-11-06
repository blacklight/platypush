<template>
  <div class="extension fade-in" :class="{hidden: !expanded}">
    <div class="row">
      <div class="col-3">
      </div>
      <div class="col-6 buttons">
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
      <VolumeSlider :value="status.volume" :range="volumeRange" :status="status"
        @mute="$emit('mute')" @unmute="$emit('unmute')"
        @set-volume="$emit('set-volume', $event)" />

      <ExtraControls :status="status" :buttons="buttons_"
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
      <button @click="$emit(status.state === 'play' ? 'pause' : 'play')"
              :title="status.state === 'play' ? 'Pause' : 'Play'">
        <i class="icon play-pause fa fa-pause" v-if="status.state === 'play'"></i>
        <i class="icon play-pause fa fa-play" v-else></i>
      </button>
    </div>

    <div class="track-container col-s-9 col-m-9 col-l-3">
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
import ProgressBar from "./ProgressBar";
import VolumeSlider from "./VolumeSlider";

export default {
  components: {ExtraControls, ProgressBar, VolumeSlider},
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
  padding: .5em;

  @include until($desktop) {
    display: flex;
  }

  :deep(.extra-controls-container) {
    @extend .pull-right;
    flex: 1;
  }

  .row {
    display: flex;
  }

  .buttons {
    display: flex;
    justify-content: center;
    margin: 0;
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

  .right-controls {
    @extend .pull-right;

    display: flex;
    flex-direction: column;
    flex: 1;
    align-items: end;

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

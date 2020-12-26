<template>
  <Loading v-if="loading" />

  <MediaView :plugin-name="pluginName" :status="status" :track="track" @play="$emit('play', $event)"
             @pause="$emit('pause')" @stop="$emit('stop')" @previous="$emit('previous')" @next="$emit('next')"
             @set-volume="$emit('set-volume', $event)" @seek="$emit('seek', $event)" @consume="$emit('consume', $event)"
             @repeat="$emit('repeat', $event)" @random="$emit('random', $event)" v-else>
    <main>
      <div class="nav-container">
        <Nav :selected-view="selectedView" @input="selectedView = $event" />
      </div>

      <div class="view-container">
        <Playlist :tracks="tracks" :status="status" :loading="loading" v-if="selectedView === 'playing'"
                  @play="$emit('play', $event)" @clear="$emit('clear')" />
      </div>
    </main>
  </MediaView>
</template>

<script>
import MediaView from "@/components/Media/View";
import Nav from "@/components/panels/Music/Nav";
import Playlist from "@/components/panels/Music/Playlist";
import Utils from "@/Utils";

export default {
  name: "Music",
  emits: ['play', 'pause', 'stop', 'clear', 'previous', 'next', 'set-volume', 'seek', 'consume', 'repeat', 'random',
          'status-update', 'playlist-update', 'new-playing-track'],
  mixins: [Utils],
  components: {Nav, MediaView, Playlist},
  props: {
    pluginName: {
      type: String,
      required: true,
    },

    loading: {
      type: Boolean,
      default: false,
    },

    config: {
      type: Object,
      default: () => {},
    },

    tracks: {
      type: Array,
      default: () => [],
    },

    status: {
      type: Object,
      default: () => {},
    },
  },

  data() {
    return {
      selectedView: 'playing',
    }
  },

  computed: {
    track() {
      if (this.status?.playingPos == null)
        return null

      return this.tracks[this.status.playingPos]
    }
  },

  methods: {
    async onStatusEvent(event) {
      if (event.plugin_name !== this.pluginName)
        return

      this.$emit('status-update', event)
    },

    async onPlaylistEvent(event) {
      if (event.plugin_name !== this.pluginName)
        return

      this.$emit('playlist-update', event)
    },

    async onNewPlayingTrack(event) {
      if (event.plugin_name !== this.pluginName)
        return

      this.notify({
        title: event.track?.artist,
        text: event.track?.title,
        iconClass: 'fa fa-play',
      })

      this.$emit('new-playing-track', event)
    },
  },

  mounted() {
    this.subscribe(this.onStatusEvent, 'on-status-update',
        'platypush.message.event.music.MusicPlayEvent',
        'platypush.message.event.music.MusicPauseEvent',
        'platypush.message.event.music.MusicStopEvent',
        'platypush.message.event.music.SeekChangeEvent',
        'platypush.message.event.music.VolumeChangeEvent',
        'platypush.message.event.music.MuteChangeEvent',
        'platypush.message.event.music.PlaybackRepeatModeChangeEvent',
        'platypush.message.event.music.PlaybackRandomModeChangeEvent',
        'platypush.message.event.music.PlaybackConsumeModeChangeEvent',
        'platypush.message.event.music.PlaybackSingleModeChangeEvent',
    )

    this.subscribe(this.onPlaylistEvent, 'on-playlist-update',
        'platypush.message.event.music.PlaylistChangeEvent')

    this.subscribe(this.onPlaylistEvent, 'on-new-playing-track',
        'platypush.message.event.music.NewPlayingTrackEvent')
  },

  unmounted() {
    this.unsubscribe('on-status-update')
    this.unsubscribe('on-playlist-update')
  },
}
</script>

<style lang="scss" scoped>
main {
  height: 100%;
  background: $background-color;
  display: flex;
  flex-direction: row-reverse;

  .view-container {
    display: flex;
    flex-grow: 1;
    overflow: auto;
  }

  ::v-deep button {
    background: rgba(0, 0, 0, 0);
  }
}
</style>

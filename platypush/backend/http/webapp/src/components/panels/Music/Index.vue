<template>
  <Loading v-if="loading" />

  <MediaView :plugin-name="pluginName" :status="status" :track="track" @play="$emit('play', $event)"
             @pause="$emit('pause')" @stop="$emit('stop')" @previous="$emit('previous')" @next="$emit('next')"
             @set-volume="$emit('set-volume', $event)" @seek="$emit('seek', $event)" @consume="$emit('consume', $event)"
             @repeat="$emit('repeat', $event)" @random="$emit('random', $event)" @search="search" v-else>
    <main>
      <div class="nav-container">
        <Nav :selected-view="selectedView" @input="selectedView = $event" />
      </div>

      <div class="view-container">
        <Playlist :tracks="tracks" :status="status" :loading="loading" :devices="devices"
                  :selected-device="selectedDevice" :active-device="activeDevice" v-if="selectedView === 'playing'"
                  @play="$emit('play', $event)" @clear="$emit('clear')" @swap="$emit('swap-tracks', $event)"
                  @add="$emit('add-to-tracklist', $event)" @remove="$emit('remove-from-tracklist', $event)"
                  @move="$emit('tracklist-move', $event)" @save="$emit('tracklist-save', $event)"
                  @info="$emit('info', $event)" @add-to-playlist="openAddToPlaylist" @search="search"
                  @refresh-status="refreshStatus" @select-device="selectDevice" />

        <Playlists :playlists="playlists" :loading="loading" :devices="devices"
                   :selected-device="selectedDevice" :active-device="activeDevice" v-else-if="selectedView === 'playlists'"
                   :edited-playlist="editedPlaylist" :tracks="editedPlaylistTracks"
                   @play="$emit('play-playlist', $event)" @load="$emit('load-playlist', $event)"
                   @remove="$emit('remove-playlist', $event)" @playlist-edit="$emit('playlist-edit', $event)"
                   @load-track="$emit('add-to-tracklist-from-edited-playlist', $event)"
                   @remove-track="$emit('remove-from-playlist', $event)" @info="$emit('info', $event)"
                   @playlist-add="$emit('playlist-add', $event)" @add-to-playlist="openAddToPlaylist"
                   @track-move="$emit('playlist-track-move', $event)" @search="search"
                   @refresh-status="refreshStatus" @select-device="selectDevice" />

        <Search :loading="loading" v-else-if="selectedView === 'search'" :devices="devices"
                :selected-device="selectedDevice" :active-device="activeDevice" @search="search"
                :results="searchResults" @clear="$emit('search-clear')" @info="$emit('info', $event)"
                @play="$emit('play', $event)" @load="$emit('add-to-tracklist', $event)"
                @add-to-playlist="openAddToPlaylist" @refresh-status="refreshStatus" @select-device="selectDevice" />

        <Library :loading="loading" v-else-if="selectedView === 'library'" :devices="devices"
                 :selected-device="selectedDevice" :active-device="activeDevice" @search="search"
                 :results="libraryResults" :path="path" @clear="$emit('search-clear')" @info="$emit('info', $event)"
                 @play="$emit('play', $event)" @load="$emit('add-to-tracklist', $event)"
                 @add-to-playlist="openAddToPlaylist" @cd="$emit('cd', $event)" @refresh-status="refreshStatus"
                 @select-device="selectDevice" />
      </div>
    </main>
  </MediaView>

  <div class="track-info-container">
    <Modal title="Track info" ref="trackInfo">
      <div class="track-info-content" v-if="trackInfo">
        <div class="row file" v-if="trackInfo.file">
          <div class="col-3 attr">File</div>
          <div class="col-9 value" v-text="trackInfo.file" />
        </div>

        <div class="row artist" v-if="trackInfo.artist">
          <div class="col-3 attr">Artist</div>
          <div class="col-9 value">
            <a :href="$route.fullPath" v-text="trackInfo.artist" @click.prevent="search({artist: trackInfo.artist})" />
          </div>
        </div>

        <div class="row track-title" v-if="trackInfo.title">
          <div class="col-3 attr">Title</div>
          <div class="col-9 value" v-text="trackInfo.title" />
        </div>

        <div class="row album" v-if="trackInfo.album">
          <div class="col-3 attr">Album</div>
          <div class="col-9 value">
            <a :href="$route.fullPath" v-text="trackInfo.album"
               @click.prevent="search({artist: trackInfo.artist, album: trackInfo.album})" />
          </div>
        </div>

        <div class="row date" v-if="trackInfo.date">
          <div class="col-3 attr">Date</div>
          <div class="col-9 value" v-text="trackInfo.date" />
        </div>

        <div class="row duration" v-if="trackInfo.time">
          <div class="col-3 attr">Duration</div>
          <div class="col-9 value" v-text="convertTime(trackInfo.time)" />
        </div>

        <div class="row track" v-if="trackInfo.track">
          <div class="col-3 attr">Track</div>
          <div class="col-9 value" v-text="trackInfo.track" />
        </div>

        <div class="row disc" v-if="trackInfo.disc">
          <div class="col-3 attr">Disc</div>
          <div class="col-9 value" v-text="trackInfo.disc" />
        </div>

        <div class="row url" v-if="trackInfo.url">
          <div class="col-3 attr">URL</div>
          <div class="col-9 value">
            <a :href="trackInfo.url" v-text="trackInfo.uri || trackInfo.url" target="_blank" />
          </div>
        </div>
      </div>
    </Modal>
  </div>

  <div class="playlists-modal-container">
    <Modal title="Playlists" ref="playlistsModal" @close="addToPlaylistTrack = null"
           @open="selectedPlaylists = [...Array(playlists.length).keys()].map(() => false)">
      <div class="filter">
        <label>
          <input type="search" placeholder="Filter" v-model="playlistFilter">
        </label>
      </div>

      <div class="playlists">
        <label class="row playlist" v-for="(playlist, i) in playlists" :key="i"
               :class="{hidden: playlistFilter?.length > 0 && playlist.name.toLowerCase().indexOf(playlistFilter.toLowerCase()) < 0}">
          <input type="checkbox" :checked="selectedPlaylists[i]"
                 @change="selectedPlaylists[i] = $event.target.checked" />
          <span class="name" v-text="playlist.name" />
        </label>
      </div>

      <FormFooter>
        <button @click="addToPlaylist">
          <i class="fa fa-plus" /> &nbsp; Add
        </button>
      </FormFooter>
    </Modal>
  </div>
</template>

<script>
import FormFooter from "@/components/elements/FormFooter";
import Loading from "@/components/Loading";
import Modal from "@/components/Modal";
import MediaUtils from "@/components/Media/Utils";
import MediaView from "@/components/Media/View";
import Nav from "@/components/panels/Music/Nav";
import Playlist from "@/components/panels/Music/Playlist";
import Playlists from "@/components/panels/Music/Playlists";
import Search from "@/components/panels/Music/Search";
import Library from "@/components/panels/Music/Library";
import Utils from "@/Utils";

export default {
  name: "Music",
  emits: ['play', 'pause', 'stop', 'clear', 'previous', 'next', 'set-volume', 'seek', 'consume', 'repeat', 'random',
    'status-update', 'playlist-update', 'new-playing-track', 'add-to-tracklist', 'remove-from-tracklist',
    'swap-tracks', 'play-playlist', 'load-playlist', 'remove-playlist', 'tracklist-move', 'tracklist-save',
    'add-to-tracklist-from-edited-playlist', 'remove-from-playlist', 'info', 'playlist-add', 'add-to-playlist',
    'playlist-track-move', 'search', 'search-clear', 'cd', 'refresh-status', 'select-device'],

  mixins: [Utils, MediaUtils],
  components: {Loading, Modal, Nav, MediaView, Playlist, Playlists, FormFooter, Search, Library},
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

    editedPlaylistTracks: {
      type: Array,
      default: () => [],
    },

    playlists: {
      type: Array,
      default: () => [],
    },

    status: {
      type: Object,
      default: () => {},
    },

    editedPlaylist: {
      type: Number,
    },

    trackInfo: {
      type: String,
    },

    searchResults: {
      type: Array,
    },

    libraryResults: {
      type: Array,
    },

    path: {
      type: String,
    },

    devices: {
      type: Object,
    },

    activeDevice: {
      type: String,
    },

    selectedDevice: {
      type: String,
    },
  },

  data() {
    return {
      selectedView: 'playing',
      selectedPlaylists: [],
      addToPlaylistTrack: null,
      playlistFilter: '',
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
        html: `<b>${event.track?.artist}</b><br>${event.track?.title}`,
        image: {
          iconClass: 'fa fa-play',
        },
      })

      this.$emit('new-playing-track', event)
    },

    async openAddToPlaylist(track) {
      this.addToPlaylistTrack = track
      this.$refs.playlistsModal.isVisible = true
    },

    async addToPlaylist() {
      this.$emit('add-to-playlist', {
        track: this.addToPlaylistTrack,
        playlists: [...Array(this.selectedPlaylists.length).keys()].filter((i) => this.selectedPlaylists[i])
      })

      this.$refs.playlistsModal.isVisible = false
      this.addToPlaylistTrack = null
      this.playlistFilter = ''
    },

    async search(filter) {
      this.$emit('search', filter)
      this.$refs.trackInfo.isVisible = false
      this.selectedView = 'search'
    },

    selectDevice(id) {
      this.$emit('select-device', id)
    },

    refreshStatus() {
      this.$emit('refresh-status')
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

    this.subscribe(this.onNewPlayingTrack, 'on-new-playing-track',
        'platypush.message.event.music.NewPlayingTrackEvent')

    this.$watch(() => this.trackInfo, (info) => {
      if (info != null)
        this.$refs.trackInfo.isVisible = true
    })
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

  ::v-deep(button) {
    background: none;
    padding: .5em .75em;
    border: 0;

    &:hover {
      border: 0;
      color: $default-hover-fg;
    }
  }

  ::v-deep(a) {
    color: $default-fg;
    opacity: 0.65;

    &:hover {
      opacity: 0.75;
      border-bottom: 1px dotted;
    }
  }
}

.playlists-modal-container {
  ::v-deep(.body) {
    display: flex;
    flex-direction: column;
    padding: 0 !important;
  }

  ::v-deep(.filter) {
    padding: .33em;
    background-color: $default-bg-6;
    border-bottom: $default-border-2;

    input {
      width: 90%;
    }
  }

  ::v-deep(.playlists) {
    overflow: auto;
    padding: 1.5em;

    label {
      display: flex;
      align-items: center;

      &:not(:last-child) {
        margin-bottom: .5em;
      }

      .name {
        margin-left: .5em;
      }
    }
  }
}

.track-info-container {
  ::v-deep(.body) {
    height: 15em;
    overflow: auto;

    @include until($tablet) {
      width: 25em;
    }

    @include from($tablet) {
      width: 35em;
    }

    .file {
      user-select: text;
    }
  }
}
</style>

<template>
  <Loading v-if="loading" />

  <div class="editor-container fade-in" v-else-if="editedPlaylist != null">
    <Playlist
      :tracks="tracks || []"
      :status="status"
      :devices="devices"
      :selected-device="selectedDevice"
      :active-device="activeDevice"
      :show-nav-button="showNavButton"
      :with-add-to-queue="true"
      :with-back="true"
      @add="$emit('playlist-add', $event)"
      @add-to-playlist="$emit('add-to-playlist', $event)"
      @add-to-queue="$emit('load-tracks', {tracks: $event, play: false})"
      @add-to-queue-and-play="$emit('load-tracks', {tracks: $event, play: true})"
      @back="$emit('playlist-edit', null)"
      @download="$emit('download', $event)"
      @info="$emit('info', $event)"
      @move="$emit('track-move', {...$event, playlist: editedPlaylist})"
      @play="$emit('load-tracks', {tracks: [$event], play: true})"
      @refresh-status="$emit('refresh-status')"
      @remove="$emit('remove-track', $event)"
      @search="$emit('search', $event)"
      @select-device="$emit('select-device', $event)"
      @toggle-nav="$emit('toggle-nav')" />
  </div>

  <div class="playlists fade-in" v-else>
    <div class="header-container">
      <MusicHeader ref="header">
        <div class="col-7 filter">
          <label>
            <input type="search" placeholder="Filter" v-model="filter">
          </label>
        </div>

        <div class="col-5 buttons">
          <Dropdown title="Players" icon-class="fa fa-volume-up" v-if="Object.keys(devices || {}).length">
            <DropdownItem v-for="(device, id) in devices" :key="id" v-text="device.name"
                          :item-class="{active: activeDevice === id, selected: selectedDevice === id}"
                          icon-class="fa fa-volume-up" @input="$emit('select-device', id)" />
          </Dropdown>

          <button title="Refresh status" @click="$emit('refresh-status')" v-if="devices != null">
            <i class="fa fa-sync"></i>
          </button>

          <button class="mobile" title="Menu" @click="$emit('toggle-nav')" v-if="showNavButton">
            <i class="fas fa-bars" />
          </button>
        </div>
      </MusicHeader>
    </div>

    <div class="body" ref="body">
      <div class="no-content" v-if="!playlists?.length">
        No playlists found
      </div>

      <div class="row playlist" :class="{hidden: !displayedPlaylists.has(i)}"
           v-for="(playlist, i) in playlists" :key="i" @click="$emit('playlist-edit', i)"
           @dblclick="$emit('load', i)">
        <div class="col-10 name-container">
          <div class="icon">
            <i class="fa fa-list" />
          </div>
          <div class="name" v-text="playlist.name || '[No Name]'" />
        </div>

        <div class="col-2 right-side">
          <span class="actions">
            <Dropdown title="Actions" icon-class="fa fa-ellipsis-h">
              <DropdownItem text="Play" icon-class="fa fa-play" @click.stop="$emit('play', i)" />
              <DropdownItem text="Load" icon-class="fa fa-list-ul" @click.stop="$emit('load', i)" />
              <DropdownItem text="Edit" icon-class="fa fa-edit" @click.stop="$emit('playlist-edit', i)" />
              <DropdownItem text="Remove" icon-class="fa fa-trash" @click.stop="$emit('remove', i)" />
            </Dropdown>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import MusicHeader from "@/components/panels/Music/Header";
import MediaUtils from "@/components/Media/Utils";
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";
import Loading from "@/components/Loading";
import Playlist from "./Playlist";

export default {
  name: "Playlists",
  mixins: [MediaUtils],
  components: {
    Dropdown,
    DropdownItem,
    MusicHeader,
    Loading,
    Playlist,
  },

  emits: [
    'add-to-playlist',
    'download',
    'info',
    'load',
    'load-tracks',
    'play',
    'playlist-add',
    'playlist-edit',
    'refresh-status',
    'remove',
    'remove-track',
    'search',
    'select-device',
    'track-move',
  ],

  props: {
    playlists: {
      type: Array,
      default: () => [],
    },

    loading: {
      type: Boolean,
      default: false,
    },

    tracks: {
      type: Array,
      default: () => [],
    },

    editedPlaylist: {
      type: Number,
    },

    devices: {
      type: Object,
    },

    status: {
      type: Object,
      default: () => {},
    },

    selectedDevice: {
      type: String,
    },

    activeDevice: {
      type: String,
    },

    showNavButton: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      selectedTracks: [],
      filter: '',
      trackFilter: '',
      sourcePos: null,
      targetPos: null,
    }
  },

  computed: {
    selectedTracksSet() {
      return new Set(this.selectedTracks)
    },

    displayedPlaylists() {
      const positions = [...Array(this.playlists.length).keys()]
      if (!this.filter?.length)
        return new Set(positions)

      const self = this
      const filter = (self.filter || '').toLowerCase()

      return new Set(
          positions.filter((pos) => {
            const track = this.playlists[pos]
            return (track?.name || '').toLowerCase().indexOf(filter) >= 0
          })
      )
    },

    displayedTracks() {
      const positions = [...Array(this.tracks.length).keys()]
      if (!this.trackFilter?.length)
        return new Set(positions)

      const self = this
      const filter = (self.trackFilter || '').toLowerCase()

      return new Set(
          positions.filter((pos) => {
            const track = this.tracks[pos]
            return (track?.artist || '').toLowerCase().indexOf(filter) >= 0
                || (track?.title || '').toLowerCase().indexOf(filter) >= 0
                || (track?.album || '').toLowerCase().indexOf(filter) >= 0
          })
      )
    },
  },

  methods: {
    onTrackClick(event, pos) {
      if (event.shiftKey) {
        const selectedTracks = this.selectedTracks.sort()
        if (!selectedTracks.length) {
          this.selectedTracks = [pos]
        } else if (pos < selectedTracks[0]) {
          this.selectedTracks = [
            ...this.selectedTracks,
            ...[...Array(selectedTracks[0] - pos).keys()].map((i) => i + pos)
          ]
        } else if (pos > selectedTracks[selectedTracks.length - 1]) {
          this.selectedTracks = [
            ...this.selectedTracks,
            ...[...Array(pos - selectedTracks[selectedTracks.length - 1] + 1).keys()].
            map((i) => i + selectedTracks[selectedTracks.length - 1])
          ]
        }
      } else {
        const idx = this.selectedTracks.indexOf(pos)
        if (event.ctrlKey) {
          if (idx >= 0)
            this.selectedTracks.splice(idx, 1)
          else
            this.selectedTracks.push(pos)
        } else {
          if (idx >= 0)
            this.selectedTracks = []
          else
            this.selectedTracks = [pos]
        }
      }
    },

    onTrackDragStart(track) {
      this.sourcePos = track
    },

    onTrackDragEnd() {
      this.$refs.editor.querySelectorAll('.track').forEach((track) => track.classList.remove('dragover'));
      if (this.sourcePos == null || this.targetPos == null || this.sourcePos === this.targetPos)
        return

      this.$emit('track-move', {from: this.selectedTracks, to: this.targetPos, playlist: this.editedPlaylist})
      this.sourcePos = null
      this.targetPos = null
      this.selectedTracks = []
    },

    onTrackDragOver(track) {
      this.targetPos = track
      const tracks = this.$refs.editor.querySelectorAll('.track')
      tracks.forEach((track) => track.classList.remove('dragover'));
      [...tracks][track].classList.add('dragover')
    },

  },
}
</script>

<style lang="scss" scoped>
@import 'vars.scss';
@import 'track.scss';
@import '../../Media/vars.scss';

.playlists {
  width: 100%;
  display: flex;
  flex-direction: column;

  .header-container {
    .filter {
      input {
        width: 100%;
      }
    }
  }

  .body {
    height: calc(100% - #{$music-header-height} - #{$media-ctrl-panel-height});
    overflow: auto;
  }

  .no-content {
    height: 100%;
  }

  .playlist {
    display: flex;
    justify-content: center;
    padding: .75em .25em .25em .25em;
    box-shadow: 0 2.5px 2px -1px $default-shadow-color;
    cursor: pointer;

    .name-container {
      display: flex;
      align-items: center;

      .icon {
        margin-right: .5em;
        opacity: .85;
      }

      .name {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }

    &:hover {
      background: $hover-bg;
    }

    &.active {
      background: $active-bg;
    }

    &.selected {
      background: $selected-bg;
    }

    .right-side {
      display: flex;
      justify-content: flex-end;
    }
  }

  .header {
    .buttons {
      display: flex;
      align-items: flex-end;
      justify-content: flex-end;
    }
  }
}

.editor-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;

  .header-container {
    width: 100%;
  }

  :deep(.header) {
    .back-btn {
      padding-left: .25em;
    }

    .search-box {
      input {
        width: 65%;
      }
    }
  }

  .editor {
    width: 100%;
    height: calc(100% - #{$music-header-height} - #{$media-ctrl-panel-height});
    display: flex;
    flex-direction: column;
    overflow: auto;
  }
}
</style>

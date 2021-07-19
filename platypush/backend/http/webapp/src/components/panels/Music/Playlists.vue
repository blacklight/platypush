<template>
  <Loading v-if="loading" />

  <div class="editor-container fade-in" v-else-if="editedPlaylist != null">
    <div class="header-container">
      <MusicHeader ref="header">
        <div class="col-8 filter">
          <button class="back-btn" title="Back" @click="$emit('playlist-edit', null)">
            <i class="fas fa-arrow-left" />
          </button>

          <label class="search-box">
            <input type="search" placeholder="Filter" v-model="trackFilter">
          </label>
        </div>

        <div class="buttons pull-right">
          <Dropdown title="Players" icon-class="fa fa-volume-up" v-if="Object.keys(devices || {}).length">
            <DropdownItem v-for="(device, id) in devices" :key="id" v-text="device.name"
                          :item-class="{active: activeDevice === id, selected: selectedDevice === id}"
                          icon-class="fa fa-volume-up" @click="$emit('select-device', id)" />
          </Dropdown>

          <button title="Refresh status" @click="$emit('refresh-status')" v-if="devices != null">
            <i class="fa fa-sync"></i>
          </button>

          <button class="add-btn" title="Add track" @click="addTrack">
            <i class="fas fa-plus" />
          </button>
        </div>
      </MusicHeader>
    </div>

    <div class="editor" ref="editor">
      <div class="no-content" v-if="!tracks?.length">
        No tracks found
      </div>

      <div class="row track" draggable="true" v-for="(track, i) in tracks" :key="i"
           :class="{selected: selectedTracksSet.has(i), active: status?.playingPos === i, hidden: !displayedTracks.has(i)}"
           @dragstart="onTrackDragStart(i)" @dragend="onTrackDragEnd(i)" @dragover="onTrackDragOver(i)"
           @click="onTrackClick($event, i)" @dblclick="$emit('load-track', {pos: i, play: true})">
        <div class="col-10">
          <div class="title">
            {{ track.title || '[No Title]' }}
          </div>

          <div class="artist" v-if="track.artist">
            <a :href="$route.fullPath" v-text="track.artist" @click.prevent="$emit('search', {artist: track.artist})" />
          </div>

          <div class="album" v-if="track.album">
            <a :href="$route.fullPath" v-text="track.album"
               @click.prevent="$emit('search', {artist: track.artist, album: track.album})" />
          </div>
        </div>

        <div class="col-2 right-side">
          <span class="duration" v-text="track.time ? convertTime(track.time) : '-:--'" />

          <span class="actions">
          <Dropdown title="Actions" icon-class="fa fa-ellipsis-h">
            <DropdownItem text="Play" icon-class="fa fa-play" @click="$emit('load-track', {pos: i, play: true})" />
            <DropdownItem text="Add to queue" icon-class="fa fa-plus" @click="$emit('load-track', {pos: i, play: false})" />
            <DropdownItem text="Add to playlist" icon-class="fa fa-list-ul" @click="$emit('add-to-playlist', track)" />
            <DropdownItem text="Remove" icon-class="fa fa-trash" @click="$emit('remove-track', [...(new Set([...selectedTracks, i]))])" />
            <DropdownItem text="Info" icon-class="fa fa-info" @click.stop="$emit('info', tracks[i])" />
          </Dropdown>
        </span>
        </div>
      </div>
    </div>
  </div>

  <div class="playlists fade-in" v-else>
    <div class="header-container">
      <MusicHeader ref="header">
        <div class="col-8 filter">
          <label>
            <input type="search" placeholder="Filter" v-model="filter">
          </label>
        </div>

        <div class="col-4 buttons">
          <Dropdown title="Players" icon-class="fa fa-volume-up" v-if="Object.keys(devices || {}).length">
            <DropdownItem v-for="(device, id) in devices" :key="id" v-text="device.name"
                          :item-class="{active: activeDevice === id, selected: selectedDevice === id}"
                          icon-class="fa fa-volume-up" @click="$emit('select-device', id)" />
          </Dropdown>

          <button title="Refresh status" @click="$emit('refresh-status')" v-if="devices != null">
            <i class="fa fa-sync"></i>
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
        <div class="col-10">
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

export default {
  name: "Playlists",
  mixins: [MediaUtils],
  components: {DropdownItem, Dropdown, MusicHeader, Loading},
  emits: ['play', 'load', 'remove', 'playlist-edit', 'search', 'remove-track', 'load-track', 'info',
    'playlist-add', 'add-to-playlist', 'track-move', 'refresh-status', 'select-device'],

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

    selectedDevice: {
      type: String,
    },

    activeDevice: {
      type: String,
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

    addTrack() {
      const track = prompt('Track path or URL')
      if (!track?.length)
        return

      this.$emit('playlist-add', track)
    },

    onTrackDragStart(track) {
      this.sourcePos = track
    },

    onTrackDragEnd() {
      this.$refs.editor.querySelectorAll('.track').forEach((track) => track.classList.remove('dragover'));
      if (this.sourcePos == null || this.targetPos == null || this.sourcePos === this.targetPos)
        return

      this.$emit('track-move', {from: this.sourcePos, to: this.targetPos, playlist: this.editedPlaylist})
      this.sourcePos = null
      this.targetPos = null
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

  ::v-deep(.header) {
    .back-btn {
      padding-left: .25em;
    }

    .add-btn {
      float: right;
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

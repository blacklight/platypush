<template>
  <Loading v-if="loading" />

  <div class="playlist fade-in" v-else>
    <div class="header-container">
      <MusicHeader ref="header">
        <div class="col-7 filter">
          <label>
            <input type="search" placeholder="Filter" v-model="filter">
          </label>
        </div>

        <div class="col-5 buttons">
          <button class="mobile" title="Menu" @click="$emit('toggle-nav')" v-if="showNavButton">
            <i class="fas fa-bars" />
          </button>

          <Dropdown title="Actions" icon-class="fa fa-ellipsis-h">
            <DropdownItem text="Add track" icon-class="fa fa-plus" @click="addTrack" />
            <DropdownItem text="Refresh status" icon-class="fa fa-sync" @click="$emit('refresh-status')" v-if="devices != null" />
            <DropdownItem text="Save as playlist" icon-class="fa fa-save" :disabled="!tracks?.length"
                          @click="playlistSave" />
            <DropdownItem text="Swap tracks" icon-class="fa fa-retweet" v-if="selectedTracks?.length === 2"
                          @click="$emit('swap', selectedTracks)" />
            <DropdownItem :text="selectionMode ? 'End selection' : 'Start selection'" icon-class="far fa-check-square"
                          :disabled="!tracks?.length" @click="selectionMode = !selectionMode" />
            <DropdownItem :text="selectedTracks?.length === tracks?.length ? 'Unselect all' : 'Select all'"
                          icon-class="fa fa-check-double" :disabled="!tracks?.length"
                          @click="selectedTracks = selectedTracks.length === tracks.length ? [] : [...Array(tracks.length).keys()]" />
            <DropdownItem :text="'Remove track' + (selectedTracks.length > 1 ? 's' : '')"
                          icon-class="fa fa-trash" v-if="selectedTracks.length > 0"
                          @click="$emit('remove', [...(new Set(selectedTracks))])" />
            <DropdownItem text="Clear playlist" icon-class="fa fa-ban" :disabled="!tracks?.length" @click="$emit('clear')" />
          </Dropdown>

          <Dropdown title="Players" icon-class="fa fa-volume-up" v-if="Object.keys(devices || {}).length">
            <DropdownItem v-for="(device, id) in devices" :key="id" v-text="device.name"
                          :item-class="{active: activeDevice === id, selected: selectedDevice === id}"
                          icon-class="fa fa-volume-up" @click="$emit('select-device', id)" />
          </Dropdown>
        </div>
      </MusicHeader>
    </div>

    <div class="body" ref="body" @scroll="onScroll">
      <div class="no-content" v-if="!tracks?.length">
        No tracks are loaded
      </div>

      <div class="row track"
           @dragstart="onTrackDragStart(i)"
           @dragend="onTrackDragEnd(i)"
           @dragover="onTrackDragOver(i)"
           draggable="true"
           v-for="i in displayedTrackIndices"
           :set="track = tracks[i]"
           :key="i"
           :data-index="i"
           :class="trackClass(i)"
           @click="onTrackClick($event, i)"
           @dblclick="$emit('play', {pos: i})">
        <div class="col-10">
          <div class="title">
            {{ track.title || '[No Title]' }}
            <div class="playing-icon" :class="{paused: status?.state === 'pause'}"
                 v-if="status?.playingPos === i && (status?.state === 'play' || status?.state === 'pause')">
              <span v-for="i in [...Array(3).keys()]" :key="i" />
            </div>
          </div>

          <div class="artist" v-if="track.artist">
            <a :href="$route.fullPath" v-text="track.artist"
               @click.prevent="$emit('search', {artist: track.artist})" />
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
              <DropdownItem text="Play" icon-class="fa fa-play" @click="$emit('play', {pos: i})" />
              <DropdownItem text="Add to playlist" icon-class="fa fa-list-ul" @click="$emit('add-to-playlist', track)" />
              <DropdownItem text="Remove" icon-class="fa fa-trash" @click="$emit('remove', [...(new Set([...selectedTracks, i]))])" />
              <DropdownItem text="Info" icon-class="fa fa-info" @click="$emit('info', tracks[i])" />
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
  name: "Playlist",
  mixins: [MediaUtils],
  components: {DropdownItem, Dropdown, MusicHeader, Loading},
  emits: [
    'add',
    'clear',
    'info',
    'move',
    'play',
    'refresh-status',
    'remove',
    'save',
    'search',
    'select-device',
    'swap',
    'toggle-nav',
  ],

  props: {
    tracks: {
      type: Array,
      default: () => [],
    },

    loading: {
      type: Boolean,
      default: false,
    },

    status: {
      type: Object,
      default: () => {},
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

    maxVisibleTracks: {
      type: Number,
      default: 100,
    },

    showNavButton: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      selectionMode: false,
      selectedTracks: [],
      filter: '',
      infoTrack: null,
      sourcePos: null,
      targetPos: null,
      centerPos: 0,
      mounted: false,
    }
  },

  computed: {
    selectedTracksSet() {
      return new Set(this.selectedTracks)
    },

    trackIndicesByToken() {
      const indices = {}
      this.tracks.forEach((track, i) => {
        const token = [track?.artist, track?.album, track?.title]
          .filter((field) => field?.trim()?.length)
          .map((field) => field.trim().toLowerCase())
          .join(' ')

        if (!indices[token])
          indices[token] = new Set()
        indices[token].add(i)
      })

      return indices
    },

    displayedTrackIndices() {
      let positions = [...Array(this.tracks.length).keys()]

      if (this.filter?.length) {
        const filter = this.filter?.trim()?.replace(/\s+/g, ' ').toLowerCase()
        const matchingPositions = new Set()
        Object.entries(this.trackIndicesByToken).forEach(([key, positions]) => {
          if (key.indexOf(filter) < 0)
            return

          matchingPositions.add(...positions)
        })

        positions = [...matchingPositions]
        positions.sort()
      }

      if (positions.length > this.maxVisibleTracks) {
        const offset = Math.max(0, this.centerPos - Math.floor(this.maxVisibleTracks / 2))
        positions = positions.slice(offset, offset + this.maxVisibleTracks)
      }

      return positions
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
        if (this.selectionMode || event.ctrlKey) {
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

    trackClass(i) {
      return {
        selected: this.selectedTracksSet.has(i),
        active: this.status?.playingPos === i,
      }
    },

    addTrack() {
      const track = prompt('Item path or URL')
      if (!track?.length)
        return

      this.$emit('add', track)
    },

    onTrackDragStart(track) {
      this.sourcePos = track
    },

    onTrackDragEnd() {
      this.$refs.body.querySelectorAll('.track').forEach((track) => track.classList.remove('dragover'));
      if (this.sourcePos == null || this.targetPos == null || this.sourcePos === this.targetPos)
        return

      this.$emit('move', {from: this.sourcePos, to: this.targetPos})
      this.sourcePos = null
      this.targetPos = null
    },

    onTrackDragOver(track) {
      this.targetPos = track
      const tracks = this.$refs.body.querySelectorAll('.track')
      tracks.forEach((track) => track.classList.remove('dragover'));
      [...tracks][track].classList.add('dragover')
    },

    onScroll() {
      const offset = this.$refs.body.scrollTop
      const bodyHeight = parseFloat(getComputedStyle(this.$refs.body).height)
      const scrollHeight = this.$refs.body.scrollHeight

      if (offset < 5)
        this.centerPos = Math.max(0, parseInt(this.centerPos - (this.maxVisibleTracks / 1.5)))
      else if (offset === scrollHeight - bodyHeight)
        this.centerPos = Math.min(this.tracks.length - 1, parseInt(this.centerPos + (this.maxVisibleTracks / 1.5)))
    },

    playlistSave() {
      const name = prompt('Playlist name')
      if (!name?.length)
        return

      this.$emit('save', name)
    },

    scrollToTrack(pos) {
      this.centerPos = pos || this.status?.playingPos || 0
      this.$nextTick(() => {
        if (!this.$refs.body) {
          this.$watch(() => this.$refs.body, () => {
            if (!this.mounted)
              this.scrollToTrack(pos)
          })

          return
        }

        [...this.$refs.body.querySelectorAll('.track')]
          .filter((track) => track.classList.contains('active'))
          .forEach((track) => track.scrollIntoView({block: 'center', behavior: 'smooth'}))

        this.mounted = true
      })
    },
  },

  mounted() {
    this.scrollToTrack()
    this.$watch(() => this.status, () => this.scrollToTrack())
    this.$watch(() => this.filter, (filter) => {
      if (!filter?.length)
        this.scrollToTrack()
    })
  },
}
</script>

<style lang="scss" scoped>
@import 'vars.scss';
@import 'track.scss';
@import '../../Media/vars.scss';

.playlist {
  width: 100%;
  display: flex;
  flex-direction: column;

  .header-container {
    button {
      border: 0;
      background: none;
    }

    .filter {
      input {
        width: 100%;
      }
    }

    .buttons {
      direction: rtl;

      .dropdown-container {
        direction: ltr;
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
}

.playing-icon {
  display: inline-block;
  position: relative;
  margin-left: .75em;
  width: 1.5em;
  height: 1em;

  @keyframes playing_bar {
    0% {
      height: 0
    }
    12.5% {
      height: 75%
    }
    25% {
      height: 100%
    }
    37.5% {
      height: 10%
    }
    50% {
      height: 40%
    }
    62.5% {
      height: 50%
    }
    75% {
      height: 30%
    }
    87.5% {
      height: 55%
    }
    100% {
      height: 0
    }
  }

  span {
    @include animation(0.2s);
    display: block;
    position: absolute;
    bottom: 0;
    width: .25em;
    height: 100%;
    background: $default-hover-fg-2;
    animation-name: playing_bar;
    animation-iteration-count: infinite;

    &:nth-child(1){
      left: 0;
      animation-duration: 2s;
    }

    &:nth-child(2){
      left: 6px;
      animation-duration: 4s;
    }

    &:nth-child(3){
      left: 12px;
      animation-duration: 1s;
    }
  }

  &.paused {
    span {
      animation-play-state: paused;
    }
  }
}

:deep(.track-info-content) {
  .attr {
    opacity: 0.75;
  }

  .value {
    text-align: right;
  }
}
</style>

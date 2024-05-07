<template>
  <Loading v-if="loading" />

  <div class="playlist fade-in" v-else>
    <div class="header-container">
      <MusicHeader ref="header">
        <div class="col-7 filter">
          <button class="back-btn" title="Back" @click="$emit('back')" v-if="withBack">
            <i class="fas fa-arrow-left" />
          </button>

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
                          @click="playlistSave" v-if="withSave" />
            <DropdownItem text="Swap tracks" icon-class="fa fa-retweet"
                          v-if="withSwap && selectedTracks?.length === 2"
                          @click="$emit('swap', selectedTracks)" />
            <DropdownItem :text="selectionMode ? 'End selection' : 'Start selection'" icon-class="far fa-check-square"
                          :disabled="!tracks?.length" @click="selectionMode = !selectionMode" />
            <DropdownItem :text="selectedTracks?.length === tracks?.length ? 'Unselect all' : 'Select all'"
                          icon-class="fa fa-check-double" :disabled="!tracks?.length"
                          @click="selectedTracks = selectedTracks.length === tracks.length ? [] : [...Array(tracks.length).keys()]" />
            <DropdownItem :text="'Remove track' + (selectedTracks.length > 1 ? 's' : '')"
                          icon-class="fa fa-trash" v-if="selectedTracks.length > 0"
                          @click="$emit('remove', [...(new Set(selectedTracks))])" />
            <DropdownItem text="Clear playlist" icon-class="fa fa-ban"
                          :disabled="!tracks?.length" @click="$emit('clear')" v-if="withClear" />
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
           :key="i"
           :data-index="i"
           :class="trackClass(i)"
           @click.left="onTrackClick($event, i)"
           @click.right.prevent="$refs['menu' + i][0].toggle($event)"
           @dblclick="$emit('play', {pos: i})">
        <div class="col-10">
          <div class="title">
            {{ tracks[i].title || '[No Title]' }}
            <div class="playing-icon" :class="{paused: status?.state === 'pause'}" v-if="isPlayingTrack(i)">
              <span v-for="i in [...Array(3).keys()]" :key="i" />
            </div>
          </div>

          <div class="artist" v-if="tracks[i].artist">
            <a v-text="tracks[i].artist" @click.prevent="searchArtist(tracks[i])" />
          </div>

          <div class="album" v-if="tracks[i].album">
            <a v-text="tracks[i].album" @click.prevent="searchAlbum(tracks[i])" />
          </div>
        </div>

        <div class="col-2 right-side">
          <span class="duration" v-text="tracks[i].time ? convertTime(tracks[i].time) : '-:--'" />

          <span class="actions">
            <Dropdown title="Actions" icon-class="fa fa-ellipsis-h" :ref="'menu' + i">
              <DropdownItem text="Play" icon-class="fa fa-play" @click="onMenuPlay(i)" />
              <DropdownItem text="Add to queue" icon-class="fa fa-plus"
                @click="$emit('add-to-queue', [...(new Set([...selectedTracks, i]))])" v-if="withAddToQueue" />
              <DropdownItem text="Add to playlist" icon-class="fa fa-list-ul" @click="$emit('add-to-playlist', tracks[i])" />
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
    'add-to-playlist',
    'add-to-queue',
    'add-to-queue-and-play',
    'back',
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

    withAddToQueue: {
      type: Boolean,
      default: false,
    },

    withBack: {
      type: Boolean,
      default: false,
    },

    withClear: {
      type: Boolean,
      default: false,
    },

    withSave: {
      type: Boolean,
      default: false,
    },

    withSwap: {
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
      scrollTimeout: null,
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
    getTrackElements() {
      return this.$refs.body.querySelectorAll('.track')
    },

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

    isPlayingTrack(i) {
      // If the state is not play or pause, then no track is playing.
      if (this.status?.state !== 'play' && this.status?.state !== 'pause')
        return false

      // If withAddToQueue is not enabled, then we are on the tracklist view.
      // The playing track is only highlighted if the track is playing.
      return (
        !this.withAddToQueue &&
        this.status?.playingPos === i
      )
    },

    trackClass(i) {
      return {
        selected: this.selectedTracksSet.has(i),
        active: this.isPlayingTrack(i),
      }
    },

    addTrack() {
      const track = prompt('Item path or URL')
      if (!track?.length)
        return

      this.$emit('add', track)
    },

    onMenuPlay(i) {
      if (this.withAddToQueue)
        this.$emit('add-to-queue-and-play', [...(new Set([...this.selectedTracks, i]))])
      else
        this.$emit('play', {pos: i})
    },

    onTrackDragStart(track) {
      this.sourcePos = track
      if (!this.selectedTracksSet.has(track))
        this.selectedTracks = [track]

      this.$nextTick(() => {
        const selectedTracks = [...this.getTrackElements()].filter(
          (_, i) => this.selectedTracksSet.has(i)
        )

        selectedTracks.forEach((track) => track.classList.add('dragging'))
      })
    },

    onTrackDragEnd() {
      this.getTrackElements().forEach((track) => {
        track.classList.remove('dragover')
        track.classList.remove('top')
        track.classList.remove('bottom')
      })

      if (!(this.sourcePos == null || this.targetPos == null || this.sourcePos === this.targetPos)) {
        const from = this.selectedTracks.length ? this.selectedTracks : [this.sourcePos]
        this.$emit('move', {from: from, to: this.targetPos})
      }

      this.sourcePos = null
      this.targetPos = null
      this.selectedTracks = []
      this.getTrackElements().forEach((track) => track.classList.remove('dragging'))
    },

    onTrackDragOver(track) {
      this.targetPos = track
      const tracks = this.getTrackElements()
      const trackEl = [...tracks].find((t) => parseInt(t.dataset.index || -1) === track)
      const minSelected = Math.min(...this.selectedTracks)

      tracks.forEach((track) => {
        track.classList.remove('dragover')
        track.classList.remove('top')
        track.classList.remove('bottom')
      })

      if (track === minSelected)
        return

      trackEl.classList.add('dragover')
      track > minSelected ? trackEl.classList.add('bottom') : trackEl.classList.add('top')
    },

    onScroll() {
      const offset = this.$refs.body.scrollTop
      const bodyHeight = parseFloat(getComputedStyle(this.$refs.body).height)
      const scrollHeight = this.$refs.body.scrollHeight

      if (offset < 5) {
        if (this.scrollTimeout)
          return

        this.scrollTimeout = setTimeout(() => {
          this.centerPos = Math.max(0, parseInt(this.centerPos - (this.maxVisibleTracks / 1.5)))
          this.$refs.body.scrollTop = 6
          this.scrollTimeout = null
        }, 250)
      } else if (offset >= (scrollHeight - bodyHeight - 5)) {
        if (this.scrollTimeout)
          return

        this.scrollTimeout = setTimeout(() => {
          this.centerPos = Math.min(this.tracks.length - 1, parseInt(this.centerPos + (this.maxVisibleTracks / 1.5)))
          this.scrollTimeout = null
        }, 250)
      }
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

    searchArtist(track) {
      const args = {}
      if (track.artist_uri)
        args.uris = [track.artist_uri]

      if (track.artist)
        args.artist = track.artist
      else {
        console.warn('No artist information available')
        console.debug(track)
        return
      }

      this.$emit('search', args)
    },

    searchAlbum(track) {
      const args = {}
      if (track.album_uri)
        args.uris = [track.album_uri]

      if (track.artist && track.album) {
        args.artist = track.artist
        args.album = track.album
      } else {
        console.warn('No artist/album information available')
        console.debug(track)
        return
      }

      this.$emit('search', args)
    },
  },

  mounted() {
    // Add the scrolling listeners only if we are on the queue view.
    if (!this.withAddToQueue) {
      this.scrollToTrack()
      this.$watch(() => this.status, () => this.scrollToTrack())
      this.$watch(() => this.filter, (filter) => {
        if (!filter?.length)
          this.scrollToTrack()
      })
    }
  },
}
</script>

<style lang="scss" scoped>
@import 'vars.scss';
@import 'track.scss';
@import '../../Media/vars.scss';

.playlist {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;

  .header-container {
    button {
      border: 0;
      background: none;
    }

    .filter {
      display: flex;
      flex-direction: row;
      align-items: center;

      label {
        flex-grow: 1;

        input[type="search"] {
          width: 100%;
        }
      }
    }

    .buttons {
      direction: rtl;

      .dropdown-container {
        direction: ltr;
      }
    }
  }

  :deep(.header) {
    .back-btn {
      padding-left: .25em;
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

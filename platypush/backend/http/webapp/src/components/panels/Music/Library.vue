<template>
  <div class="library fade-in">
    <Loading v-if="loading" />

    <MusicHeader>
      <label class="search-box">
        <input type="search" placeholder="Filter" v-model="filter">
      </label>
    </MusicHeader>

    <div class="results">
      <div class="row track back-track" @click="back" v-if="path !== '/'">
        <div class="icon-container">
          <i class="icon fa fa-folder" />
        </div>
        <div class="result-container">
          <div class="title">..</div>
        </div>
      </div>

      <div class="row track" :class="{selected: selectedResults.has(i), hidden: !displayedResults.has(i)}"
           v-for="(result, i) in results" :key="i" @click="resultClick(i, $event)">
        <div class="col-10 left-side">
          <div class="icon-container">
            <i class="icon fa fa-folder" v-if="result.directory" />
            <i class="icon fa fa-music" v-else-if="result.file" />
          </div>

          <div class="info">
            <div class="title">
              <span v-if="result.directory" v-text="result.directory.split('/').pop()" />
              <span v-else-if="result.title" v-text="result.title" />
            </div>

            <div class="artist-album">
              <div class="artist" v-text="result.artist" v-if="result.artist?.length" />
              <div class="album" v-text="result.album" v-if="result.album?.length" />
            </div>
          </div>
        </div>

        <div class="col-2 right-side">
          <span class="duration" v-text="result.time && parseInt(result.time) ? convertTime(result.time) : '-:--'" />

          <span class="actions">
            <Dropdown title="Actions" icon-class="fa fa-ellipsis-h">
              <DropdownItem text="Play" icon-class="fa fa-play" @click="play(i)" />
              <DropdownItem text="Add to queue" icon-class="fa fa-plus" @click="load(i)" />
              <DropdownItem text="Add to playlist" icon-class="fa fa-list-ul" @click="$emit('add-to-playlist', result)" />
              <DropdownItem text="Info" icon-class="fa fa-info" @click="$emit('info', result)" />
            </Dropdown>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";
import MediaUtils from "@/components/Media/Utils";
import MusicHeader from "@/components/panels/Music/Header";

export default {
  name: "Library",
  components: {Dropdown, DropdownItem, MusicHeader, Loading},
  mixins: [MediaUtils],
  emits: ['search', 'play', 'load', 'add-to-playlist', 'info', 'cd', 'refresh-status', 'select-device'],
  props: {
    loading: {
      type: Boolean,
      default: false,
    },

    results: {
      type: Array,
    },

    path: {
      type: String,
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
      selectedResults: new Set(),
      filter: '',
      query: {
        any: '',
        artist: '',
        title: '',
        album: '',
      },
    }
  },

  computed: {
    displayedResults() {
      return new Set([...Array(this.results?.length || 0).keys()].filter((i) => {
        const result = this.results[i]
        if (!this.filter?.length)
          return result

        const filter = this.filter.toLowerCase()
        return (result?.artist || '').toLowerCase().indexOf(filter) >= 0 ||
            (result?.title || '').toLowerCase().indexOf(filter) >= 0 ||
            (result?.album || '').toLowerCase().indexOf(filter) >= 0 ||
            (result?.directory || '').toLowerCase().indexOf(filter) >= 0
      }))
    },
  },

  methods: {
    resultClick(pos, event) {
      if (event.shiftKey) {
        if (this.selectedResults.size > 0 && !this.selectedResults.has(pos)) {
          const results = [...this.selectedResults]
          const min = Math.min(Math.min(results), pos)
          const max = Math.max(Math.max(results), pos)
          this.selectedResults = new Set([...Array(max-min+1).keys()].map((i) => i+min))
        }
      } else if (event.ctrlKey) {
        if (this.selectedResults.has(pos))
          this.selectedResults.delete(pos)
        else
          this.selectedResults.add(pos)
      } else {
        if (this.results[pos].directory) {
          this.$emit('cd', this.results[pos].directory)
        } else {
          this.selectedResults = new Set()
          if (this.selectedResults.has(pos))
            this.selectedResults.delete(pos)
          else
            this.selectedResults.add(pos)
        }
      }
    },

    play(pos) {
      this.$emit('play', this.results[pos])
      if (this.selectedResults.size)
        this.selectedResults.forEach((result) => {
          this.$emit('load', result)
        })
    },

    load(pos) {
      if (!this.selectedResults.has(pos))
        this.selectedResults.add(pos)

      this.selectedResults.forEach((i) => {
        this.$emit('load', this.results[i])
      })
    },

    back() {
      const path = this.path.split('/')
      this.$emit('cd', path.slice(0, path.length-1).join('/'))
    },
  },
}
</script>

<style lang="scss" scoped>
@import 'track.scss';

.library {
  width: 100%;
  display: flex;
  flex-direction: column;

  .results {
    overflow: auto;
    height: 100%;

    .track {
      display: flex;
      align-items: center;
      justify-content: left;

      .left-side {
        display: inline-flex;
        align-items: center;
      }
    }

    .icon {
      opacity: .5;
      margin-right: .75em;
    }
  }

  :deep(.header) {
    display: flex;
    width: 100%;
    align-items: center;

    .search-box {
      width: 70%;

      input[type=search] {
        width: 100%;
      }
    }

    .buttons {
      width: 30%;
      display: inline-flex;
      justify-content: right;
      margin: 0;
    }
  }
}
</style>

<template>
  <div class="search fade-in" :class="{'form-collapsed': formCollapsed}">
    <button class="nav-toggler mobile floating" title="Menu" @click="$emit('toggle-nav')" v-if="showNavButton && !formCollapsed">
      <i class="fas fa-bars" />
    </button>

    <div class="form-container" v-if="!formCollapsed" @submit.prevent="$emit('search', filteredQuery)">
      <form class="search-form">
        <div class="row">
          <label>
            <input type="text" placeholder="Any" v-model="query.any" />
          </label>
        </div>

        <div class="row">
          <label>
            <input type="text" placeholder="Artist" v-model="query.artist" />
          </label>
        </div>

        <div class="row">
          <label>
            <input type="text" placeholder="Title" v-model="query.title" />
          </label>
        </div>

        <div class="row">
          <label>
            <input type="text" placeholder="Album" v-model="query.album" />
          </label>
        </div>

        <FormFooter>
          <button @click="clear">
            <i class="icon fa fa-times" />
            <span class="btn-title">Clear</span>
          </button>

          <button type="submit">
            <i class="icon fa fa-search" />
            <span class="btn-title">Search</span>
          </button>
        </FormFooter>
      </form>
    </div>

    <MusicHeader v-else>
      <label class="col-10 search-box">
        <button class="back-btn" title="Back" @click="clear">
          <i class="fas fa-arrow-left" />
        </button>

        <input type="search" placeholder="Filter" v-model="filter">
      </label>

      <span class="col-2 buttons">
        <button class="mobile" title="Menu" @click="$emit('toggle-nav')" v-if="showNavButton">
          <i class="fas fa-bars" />
        </button>
      </span>
    </MusicHeader>

    <div class="results">
      <div class="row track" :class="{selected: selectedResults.has(i), hidden: !displayedTracks.has(i)}"
           v-for="(result, i) in results" :key="i" @click="resultClick(i, $event)">
        <div class="col-10">
          <div class="title-container">
            <div class="type" :title="result.type" v-if="result.type">
              <i class="fa fa-user" v-if="result.type === 'artist'" />
              <i class="fa fa-compact-disc" v-else-if="result.type === 'album'" />
              <i class="fa fa-list" v-else-if="result.type === 'playlist'" />
              <i class="fa fa-music" v-else />
            </div>

            <div class="title">
              <span v-if="result.type === 'playlist'">{{ result.name || result.title || '[No Name]' }}</span>
              <span v-else-if="result.type === 'artist'">{{ result.name || result.title || result.artist || '[No Name]' }}</span>
              <span v-else-if="result.type === 'album'">{{ result.name || result.title || result.album || '[No Title]' }}</span>
              <span v-else>{{ result.title || '[No Title]' }}</span>
            </div>
          </div>

          <div class="artist" v-text="result.artist" v-if="result.artist?.length && result.type !== 'artist'" />
          <div class="album" v-text="result.album" v-if="result.album?.length && result.type !== 'album'" />
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
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";
import FormFooter from "@/components/elements/FormFooter";
import MediaUtils from "@/components/Media/Utils";
import MusicHeader from "@/components/panels/Music/Header";

export default {
  name: "Search",
  components: {Dropdown, DropdownItem, FormFooter, MusicHeader},
  mixins: [MediaUtils],
  emits: [
    'add-to-playlist',
    'clear',
    'info',
    'load',
    'play',
    'refresh-status',
    'search',
    'select-device',
    'toggle-nav',
  ],

  props: {
    loading: {
      type: Boolean,
      default: false,
    },

    results: {
      type: Array,
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

    showNavButton: {
      type: Boolean,
      default: false,
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
    formCollapsed() {
      return this.results?.length > 0
    },

    filteredQuery() {
      return Object.entries(this.query).filter((o) => o[1]?.length).reduce((obj, [k, v]) => {
        obj[k] = v
        return obj
      }, {})
    },

    displayedTracks() {
      return new Set([...Array(this.results?.length || 0).keys()].filter((i) => {
        const result = this.results[i]
        if (!this.filter?.length)
          return result

        const filter = this.filter.toLowerCase()
        return (result?.artist || '').toLowerCase().indexOf(filter) >= 0 ||
            (result?.title || '').toLowerCase().indexOf(filter) >= 0 ||
            (result?.album || '').toLowerCase().indexOf(filter) >= 0
      }))
    },
  },

  methods: {
    clear() {
      this.$emit('clear')
      this.selectedResults = new Set()
    },

    resultClick(pos, event) {
      if (event.shiftKey) {
        if (this.selectedResults.size > 0 && !this.selectedResults.has(pos)) {
          const results = [...this.selectedResults]
          const min = Math.min(Math.min(results), pos)
          const max = Math.max(Math.max(results), pos)
          this.selectedResults = new Set([...Array(max-min+1).keys()].map((i) => i+min))
        }
      } else {
        if (!event.ctrlKey)
          this.selectedResults = new Set()
        if (this.selectedResults.has(pos))
          this.selectedResults.delete(pos)
        else
          this.selectedResults.add(pos)
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
  },
}
</script>

<style lang="scss" scoped>
@import 'vars.scss';
@import 'track.scss';
@import '../../Media/vars.scss';

.search {
  width: 100%;
  height: calc(100% - #{$media-ctrl-panel-height});
  display: flex;
  flex-direction: column;
  position: relative;

  .nav-toggler.floating {
    position: absolute;
    top: 0;
    right: 0;
    z-index: 1;
  }

  &:not(.form-collapsed) {
    justify-content: center;
    align-items: center;
  }

  .form-container {
    width: 100%;
    height: 100%;
    display: flex;
    flex-grow: 1;
    align-items: center;
    justify-content: center;
  }

  form {
    width: calc(100% - 2em);
    max-width: 30em;
    height: 17em;
    background: $default-bg-5;
    display: flex;
    flex-direction: column;
    padding: 2em;
    border-radius: 1.5em;

    .row {
      margin: .25em 0;
    }

    input[type=text] {
      width: 100%;
    }

    :deep(.form-footer) {
      height: 3em;
      padding-right: 0;
      border: 0;
    }

    :deep(button) {
      border: 0;

      &[type=submit] {
        background: none;
      }

      &:hover {
        border: 0;
        color: $default-hover-fg-2;
      }
    }
  }

  .results {
    height: calc(100% - #{$music-header-height});
    flex-grow: 1;
    overflow: auto;

    .title-container {
      display: flex;
      align-items: center;
      
      .type {
        opacity: .85;
        margin-right: .5em;
      }
    }
  }

  :deep(.header) {
    display: flex;
    width: 100%;
    align-items: center;

    .search-box {
      width: 70%;
      display: flex;
      align-items: center;

      .back-btn {
        margin-left: 0;
        padding-left: 0;
      }

      input[type=search] {
        width: 100%;
      }
    }

    .buttons {
      width: 30%;
      display: inline-flex;
      justify-content: flex-end;
      margin: 0;
    }
  }
}
</style>

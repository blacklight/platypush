<template>
  <div class="header" :class="{'with-filter': filterVisible}">
    <div class="row">
      <div class="col-7 left side" v-if="selectedView === 'search'">
        <button title="Filter" class="filter-btn" :class="{selected: filterVisible}"
                @click="filterVisible = !filterVisible">
          <i class="fa fa-filter" />
        </button>

        <form @submit.prevent="search">
          <label class="search-box">
            <input type="search" placeholder="Search" v-model="query">
          </label>
        </form>
      </div>

      <div class="col-7 left side" v-else-if="selectedView === 'torrents'">
        <form @submit.prevent="$emit('torrent-add', torrentURL)">
          <label class="search-box">
            <input type="search" placeholder="Add torrent URL" v-model="torrentURL">
          </label>
        </form>
      </div>

      <div class="col-7 left side" v-else-if="selectedView === 'browser'">
        <label class="search-box">
          <input type="search" placeholder="Filter" :value="browserFilter" @change="$emit('filter', $event.target.value)"
                 @keyup="$emit('filter', $event.target.value)">
        </label>
      </div>

      <div class="col-5 right side">
        <button title="Select subtitles" class="captions-btn" :class="{selected: selectedSubtitles != null}"
                @click="$emit('show-subtitles')" v-if="hasSubtitlesPlugin && selectedItem &&
                  (selectedItem.type === 'file' || (selectedItem.url || '').startsWith('file://'))">
          <i class="fas fa-closed-captioning" />
        </button>

        <Players :plugin-name="pluginName" @select="$emit('select-player', $event)"
                 @status="$emit('player-status', $event)" />

        <button title="Play URL" @click="$emit('play-url')">
          <i class="fa fa-plus-circle" />
        </button>
      </div>
    </div>

    <div class="row filter fade-in" :class="{hidden: !filterVisible}">
      <label v-for="source in Object.keys(sources)" :key="source">
        <input type="checkbox" :checked="sources[source]" @change="$emit('source-toggle', source)" />
        {{ source }}
      </label>
    </div>
  </div>
</template>

<script>
import Players from "@/components/panels/Media/Players";
export default {
  name: "Header",
  components: {Players},
  emits: ['search', 'select-player', 'player-status', 'torrent-add', 'show-subtitles', 'play-url', 'filter',
    'source-toggle'],

  props: {
    pluginName: {
      type: String,
      required: true,
    },

    selectedView: {
      type: String,
      required: true,
    },

    selectedSubtitles: {
      type: String,
    },

    selectedItem: {
      type: Object,
    },

    hasSubtitlesPlugin: {
      type: Boolean,
      default: false,
    },

    browserFilter: {
      type: String,
      default: '',
    },

    sources: {
      type: Object,
      default: () => {},
    }
  },

  data() {
    return {
      filterVisible: false,
      query: '',
      torrentURL: '',
    }
  },

  methods: {
    search() {
      const types = Object.keys(this.sources).filter((source) => this.sources[source])
      if (!this.query?.length || !types?.length)
        return

      this.$emit('search', {
        query: this.query,
        types: types,
      })
    },
  },

  mounted() {
    this.$watch(() => this.selectedView, () => {
      this.$emit('filter', '')
      this.torrentURL = ''
      this.query = ''
    })
  },
}
</script>

<style lang="scss" scoped>
@import "vars";

.header {
  width: 100%;
  height: $media-header-height;
  position: relative;
  background: $menu-panel-bg;
  padding: .5em;
  box-shadow: $border-shadow-bottom;

  .filter-btn.selected {
    color: $selected-fg;
  }

  .row {
    display: flex;
    align-items: center;
  }

  &.with-filter {
    height: calc(#{$media-header-height} + #{$filter-header-height});
    padding-bottom: 0;
  }

  .side {
    display: inline-flex;
    align-items: center;

    &.right {
      justify-content: right;
      direction: rtl;
    }
  }

  :deep(button) {
    background: none;
    padding: 0 .25em;
    border: 0;
    margin-right: .25em;

    &:hover {
      color: $default-hover-fg-2;
    }
  }

  form {
    width: 100%;
    padding: 0;
    border: 0;
    border-radius: 0;
    box-shadow: none;
    background: initial;
  }

  .search-box {
    width: 100%;
    margin-left: .5em;

    input[type=search] {
      width: 100%;
    }
  }

  .filter {
    width: 100%;
    height: $filter-header-height;
    margin-top: .5em;

    label {
      display: inline-flex;
      flex-direction: row;
      margin-right: 1em;

      input {
        margin-right: .5em;
      }
    }
  }

  .captions-btn {
    margin-right: .5em;

    &.selected {
      color: $selected-fg;
    }
  }
}
</style>

<template>
  <div class="header" :class="{'with-filter': filterVisible}">
    <div class="row">
      <div class="col-s-8 col-m-7 left side" v-if="selectedView === 'search'">
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

      <div class="col-s-8 col-m-7 left side" v-else-if="selectedView === 'torrents'">
        <form @submit.prevent="$emit('torrent-add', torrentURL)">
          <label class="search-box">
            <input type="search" placeholder="Add torrent URL" v-model="torrentURL">
          </label>
        </form>
      </div>

      <div class="col-s-8 col-m-7 left side" v-else-if="selectedView === 'downloads'">
        <form @submit.prevent="$emit('filter-downloads', downloadFilter)">
          <label class="search-box">
            <input type="search" placeholder="Filter" v-model="downloadFilter">
          </label>
        </form>
      </div>

      <div class="col-s-8 col-m-7 left side" v-else-if="selectedView === 'browser'">
        <label class="search-box">
          <input type="search" placeholder="Filter" :value="browserFilter" @change="$emit('filter', $event.target.value)"
                 @keyup="$emit('filter', $event.target.value)">
        </label>
      </div>

      <div class="col-s-4 col-m-5 right side">
        <button class="mobile" title="Menu" @click="$emit('toggle-nav')" v-if="showNavButton">
          <i class="fas fa-bars" />
        </button>

        <button title="Select subtitles" class="captions-btn" :class="{selected: selectedSubtitles != null}"
                @click="$emit('show-subtitles')" v-if="hasSubtitlesPlugin && selectedItem &&
                  (selectedItem.type === 'file' || (selectedItem.url || '').startsWith('file://'))">
          <i class="fas fa-closed-captioning" />
        </button>

        <Players :plugin-name="pluginName" @select="$emit('select-player', $event)"
                 @status="$emit('player-status', $event)" />

        <button title="Play URL" @click="$emit('play-url')">
          <i class="fas fa-play" />
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
import Players from "@/components/panels/Media/Players"
import Utils from '@/Utils'

export default {
  name: "Header",
  components: {Players},
  mixins: [Utils],
  emits: [
    'filter',
    'filter-downloads',
    'play-url',
    'player-status',
    'search',
    'select-player',
    'show-subtitles',
    'source-toggle',
    'toggle-nav',
    'torrent-add',
  ],

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

    showNavButton: {
      type: Boolean,
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
      downloadFilter: '',
    }
  },

  computed: {
    enabledTypes() {
      return Object.keys(this.sources).filter((source) => this.sources[source])
    },
  },

  methods: {
    search() {
      if (!this.query?.length || !this.enabledTypes?.length)
        return

      this.$emit('search', {
        query: this.query,
        types: this.enabledTypes,
      })
    },
  },

  mounted() {
    this.$nextTick(() => {
      const query = this.getUrlArgs()?.q
      if (query) {
        this.query = query
        this.$emit('search', {
          query: query,
          types: this.enabledTypes,
        })
      }
    })

    this.$watch(() => this.selectedView, () => {
      this.$emit('filter', '')
      this.torrentURL = ''
      this.query = ''
    })
  },
}
</script>

<style lang="scss" scoped>
@import "~@/components/Media/vars";

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
    padding: 0 .5em;
    border: 0;

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

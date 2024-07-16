<template>
  <nav>
    <button class="menu-button mobile" @click="$emit('toggle')">
      <i class="fa fa-bars" />
    </button>

    <li v-for="(view, name) in displayedViews" :key="name" :title="view.displayName"
        :class="{selected: name === selectedView, ...customClasses[name]}" @click="input(name)">
      <i :class="view.iconClass" />
    </li>
  </nav>
</template>

<script>
import Utils from '@/Utils';

export default {
  mixins: [Utils],
  emits: ['input', 'toggle'],
  props: {
    selectedView: {
      type: String,
    },

    collapsed: {
      type: Boolean,
      default: false,
    },

    torrentPlugin: {
      type: String,
    },

    downloadIconClass: {
      type: String,
    },

    views: {
      type: Object,
      default: () => {
        return {
          search: {
            iconClass: 'fa fa-search',
            displayName: 'Search',
          },

          browser: {
            iconClass: 'fa fa-folder',
            displayName: 'Browser',
          },

          downloads: {
            iconClass: 'fa fa-download',
            displayName: 'Downloads',
          },

          torrents: {
            iconClass: 'fa fa-magnet',
            displayName: 'Torrents',
          },
        }
      }
    },
  },

  computed: {
    displayedViews() {
      const views = {...this.views}
      if (!this.torrentPlugin?.length)
        delete views.torrents

      return views
    },

    customClasses() {
      return {
        downloads: this.downloadIconClass.split(' ').reduce((acc, cls) => {
          acc[cls] = true
          return acc
        }, {}),
      }
    },
  },

  methods: {
    input(view) {
      this.$emit('input', view)
      this.setUrlArgs({view: view})
    },
  },
}
</script>

<style lang="scss" scoped>
@import "~@/components/Media/vars";

nav {
  width: $media-nav-width;
  height: 100%;
  background: $nav-collapsed-bg;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  box-shadow: 2.5px 0 4.5px 2px $nav-collapsed-fg;
  margin-left: 2.5px;
  overflow: auto;

  .menu-button {
    position: absolute;
    top: 0.75em;
    left: 0;
    width: 100%;
    display: inline-flex;
    justify-content: center;
    padding: 0;
    margin: 0;
    font-size: 1.2em;
    border: 0;
    background: none;
    cursor: pointer;
    z-index: 1;

    &:hover {
      color: $default-hover-fg;
    }
  }

  li {
    display: flex;
    align-items: center;
    font-size: 1.2em;
    cursor: pointer;
    list-style: none;
    padding: .6em;
    opacity: 0.7;
    border-radius: 1.2em;
    margin: 0 0.2em;

    &:hover {
      background: $nav-entry-collapsed-hover-bg;
    }

    &.selected {
      background: $nav-entry-collapsed-selected-bg;
    }

    &.completed {
      color: $ok-fg;
    }
  }
}
</style>

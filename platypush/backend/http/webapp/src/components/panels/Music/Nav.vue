<template>
  <nav>
    <button class="menu-button mobile" @click="$emit('toggle')">
      <i class="fa fa-bars" />
    </button>

    <li v-for="(view, name) in views" :key="name" :title="view.displayName"
        :class="{selected: name === selectedView}" @click="$emit('input', name)">
      <i :class="view.iconClass" />
    </li>
  </nav>
</template>

<script>
export default {
  name: "Nav",
  emits: ['input', 'toggle'],
  props: {
    selectedView: {
      type: String,
    },

    collapsed: {
      type: Boolean,
      default: false,
    },

    views: {
      type: Object,
      default: () => {
        return {
          playing: {
            iconClass: 'fas fa-play',
            displayName: 'Queue',
          },

          search: {
            iconClass: 'fas fa-search',
            displayName: 'Search',
          },

          playlists: {
            iconClass: 'fas fa-list-ul',
            displayName: 'Playlists',
          },

          library: {
            iconClass: 'fas fa-compact-disc',
            displayName: 'Library',
          },
        }
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import 'vars.scss';

nav {
  width: $music-nav-width;
  height: 100%;
  position: relative;
  background: $nav-collapsed-bg;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  box-shadow: 2.5px 0 4.5px 2px $nav-collapsed-fg;
  margin-left: 2.5px;
  overflow: hidden;

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

    &.selected,
    &:hover {
      border-radius: 1.2em;
      margin: 0 0.2em;
    }

    &:hover {
      background: $nav-entry-collapsed-hover-bg;
    }

    &.selected {
      background: $nav-entry-collapsed-selected-bg;
    }

  }
}
</style>

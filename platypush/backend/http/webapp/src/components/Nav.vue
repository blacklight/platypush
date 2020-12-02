<template>
  <nav :class="{collapsed: collapsed}">
    <div class="toggler" @click="collapsed = !collapsed">
      <i class="fas fa-bars" />
      <span class="hostname" v-if="!collapsed && hostname" v-text="hostname" />
    </div>

    <li v-for="name in Object.keys(panels)" :key="name" class="entry" :class="{selected: name === selectedPanel}"
        @click="$emit('select', name)">
      <a :href="`/#${name}`">
        <span class="icon">
          <i :class="icons[name].class" v-if="icons[name]?.class" />
          <i class="fas fa-puzzle-piece" v-else />
        </span>
        <span class="name" v-if="!collapsed">{{ displayName(name) }}</span>
      </a>
    </li>
  </nav>
</template>

<script>
import { icons } from '@/assets/icons.json'

export default {
  name: "Nav",
  emits: ['select'],
  props: {
    panels: {
      type: Object,
      required: true,
    },

    selectedPanel: {
      type: String,
    },

    hostname: {
      type: String,
    },
  },

  methods: {
    displayName(name) {
      return name.split('.').map((token) => token[0].toUpperCase() + token.slice(1)).join(' ')
    },
  },

  data() {
    return {
      collapsed: false,
      icons: icons,
      host: null,
    }
  },
}
</script>

<!--suppress SassScssResolvedByNameOnly -->
<style lang="scss" scoped>
nav {
  width: 20%;
  min-width: 12.5em;
  max-width: 25em;
  height: 100%;
  overflow: auto;
  background: $nav-bg;
  color: $nav-fg;
  box-shadow: $nav-box-shadow-main;
  margin-right: 4px;

  li {
    box-shadow: $nav-box-shadow-entry;
    cursor: pointer;

    a {
      display: block;
      color: $nav-fg;
      padding: 1em 0.25em;
      &:hover {
        color: $nav-fg;
      }
    }

    &:hover {
      background: $nav-entry-hover-bg;
    }

    &.selected {
      background: $nav-entry-selected-bg;
    }

    .icon {
      margin-right: 0.5em;
    }

    .name {
      text-transform: capitalize;
    }
  }

  .toggler {
    width: 100%;
    display: flex;
    font-size: 1.5em;
    cursor: pointer;
    padding: 0.4em;

    .hostname {
      font-size: 0.7em;
      margin-left: 1em;
    }
  }

  &.collapsed {
    width: 2.5em;
    min-width: unset;
    max-width: unset;
    background: initial;
    color: $nav-collapsed-fg;
    box-shadow: $nav-box-shadow-collapsed;

    a {
      color: $nav-collapsed-fg;
      padding: 0.25em 0;
      &:hover {
        color: $nav-collapsed-fg;
      }
    }

    .toggler {
      text-align: center;
      margin-bottom: 3em;
    }

    li {
      box-shadow: none;
      padding: 0;
      text-align: center;

      &.selected,
      &:hover {
        border-radius: 1em;
        margin: 0 0.2em;
      }

      &.selected {
        background: $nav-entry-collapsed-selected-bg;
      }

      &:hover {
        background: $nav-entry-collapsed-hover-bg;
      }

      .icon {
        margin-right: 0;
      }
    }
  }
}
</style>

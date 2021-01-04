<template>
  <nav :class="{collapsed: collapsed}">
    <div class="toggler" @click="collapsed = !collapsed">
      <i class="fas fa-bars" />
      <span class="hostname" v-if="hostname" v-text="hostname" />
    </div>

    <ul>
      <li v-for="name in Object.keys(panels).sort()" :key="name" class="entry" :class="{selected: name === selectedPanel}"
          :title="name" @click="onItemClick(name)">
        <a :href="`/#${name}`">
        <span class="icon">
          <i :class="icons[name].class" v-if="icons[name]?.class" />
          <i class="fas fa-puzzle-piece" v-else />
        </span>
        <span class="name" v-if="!collapsed" v-text="name" />
        </a>
      </li>
    </ul>
  </nav>
</template>

<script>
import { icons } from '@/assets/icons.json'
import Utils from "@/Utils";

export default {
  name: "Nav",
  emits: ['select'],
  mixins: [Utils],
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
    onItemClick(name) {
      this.$emit('select', name)
      this.collapsed = true
    },
  },

  data() {
    return {
      collapsed: true,
      icons: icons,
      host: null,
    }
  },

  mounted() {
    if (this.isMobile() && !this.$root.$route.hash.length)
      this.collapsed = false
  },
}
</script>

<!--suppress SassScssResolvedByNameOnly -->
<style lang="scss" scoped>
nav {
  @media screen and (max-width: $tablet) {
    width: 100%;
    height: 100vh;
    background: $nav-bg;
    color: $nav-fg;
    box-shadow: $nav-box-shadow-main;

    &:not(.collapsed) {
      position: absolute;
      top: 0;
      left: 0;
      z-index: 2;
    }
  }

  @media screen and (min-width: $tablet) {
    width: 20%;
    min-width: 12.5em;
    max-width: 25em;
    height: 100%;
    overflow: auto;
    background: $nav-bg;
    color: $nav-fg;
    box-shadow: $nav-box-shadow-main;
    margin-right: 2px;
  }

  li {
    box-shadow: $nav-box-shadow-entry;
    cursor: pointer;
    list-style: none;

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
  }

  .toggler {
    width: 100%;
    display: flex;
    font-size: 1.5em;
    cursor: pointer;
    padding: 0.4em;
    align-items: center;
  }

  .hostname {
    font-size: 0.7em;

    @media screen and (min-width: $tablet) {
      margin-left: 1em;
    }

    @media screen and (max-width: $tablet) {
      text-align: right;
      margin-right: 0.25em;
      flex-grow: 1;
    }
  }

  &.collapsed {
    display: flex;
    flex-direction: column;

    @media screen and (min-width: $tablet) {
      width: 2.5em;
      min-width: unset;
      max-width: unset;
      background: $nav-collapsed-bg;
      color: $nav-collapsed-fg;
      box-shadow: $nav-box-shadow-collapsed;

      .hostname {
        display: none;
      }
    }

    @media screen and (max-width: $tablet) {
      height: auto;
    }

    a {
      color: $nav-collapsed-fg;
      padding: 0.25em 0;
      &:hover {
        color: $nav-collapsed-fg;
      }
    }

    .toggler {
      text-align: center;
    }

    ul {
      display: flex;
      flex-direction: column;
      justify-content: center;
      flex-grow: 1;

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

        @media screen and (max-width: $tablet) {
          display: none;
        }
      }
    }
  }
}
</style>

<template>
  <nav :class="{collapsed: collapsed}">
    <div class="toggler" @click="collapsed = !collapsed">
      <i class="fas fa-bars" />
      <span class="hostname" v-if="hostname" v-text="hostname" />
    </div>

    <ul class="plugins">
      <li v-for="name in Object.keys(panels).sort()" :key="name" class="entry" :class="{selected: name === selectedPanel}"
          :title="name" @click="onItemClick(name)">
        <a :href="`/#${name}`">
        <span class="icon">
          <i :class="icons[name].class" v-if="icons[name]?.class" />
          <img :src="icons[name].imgUrl" v-else-if="icons[name]?.imgUrl"  alt="name"/>
          <i class="fas fa-puzzle-piece" v-else />
        </span>
        <span class="name" v-if="!collapsed" v-text="name" />
        </a>
      </li>
    </ul>

    <ul class="footer">
      <li :class="{selected: selectedPanel === 'settings'}" title="Settings" @click="onItemClick('settings')">
        <!--suppress HtmlUnknownAnchorTarget -->
        <a href="/#settings">
          <span class="icon">
            <i class="fa fa-cog" />
          </span>
          <span class="name" v-if="!collapsed">Settings</span>
        </a>
      </li>

      <li title="Logout" @click="onItemClick('logout')">
        <!--suppress HtmlUnknownTarget -->
        <a href="/logout">
          <span class="icon">
            <i class="fas fa-sign-out-alt" />
          </span>
          <span class="name" v-if="!collapsed">Logout</span>
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
$toggler-height: 2em;
$footer-collapsed-height: 4em;
$footer-expanded-height: 8.25em;

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

    .name {
      margin-left: 0.5em;
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

  .plugins {
    height: calc(100% - #{$toggler-height} - #{$footer-expanded-height} - .75em);
    overflow: auto;
  }

  .footer {
    height: $footer-expanded-height;
    background: none;
    padding: 0;
    margin: 0;
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
      height: $toggler-height;
      text-align: center;
    }

    .plugins {
      height: calc(100% - #{$toggler-height} - #{$footer-collapsed-height});
      overflow: auto;
    }

    .footer {
      height: $footer-collapsed-height;
      padding: 0;
      margin-bottom: .5em;
    }

    @media screen and (max-width: $tablet) {
      .footer {
        display: none;
      }
    }

    ul {
      display: flex;
      flex-direction: column;
      justify-content: center;

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

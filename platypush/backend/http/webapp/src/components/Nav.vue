<template>
  <nav :class="{collapsed: collapsed}">
    <div class="toggler" @click="collapsed = !collapsed">
      <i class="fas fa-bars" />
      <span class="hostname" v-if="hostname" v-text="hostname" />
      <i class="icon status fas fa-circle"
         :class="{ok: connected, error: !connected}"
         :title="connected ? 'Connected' : 'Disconnected'" />
    </div>

    <ul class="plugins" v-if="selectedPanel === 'settings'">
      <li class="entry" title="Home" @click="onItemClick('entities')">
        <a href="/#">
          <i class="fas fa-home" />
          <span class="name" v-if="!collapsed">Home</span>
        </a>
      </li>

      <li v-for="config, name in configSections" :key="name" class="entry"
          :class="{selected: name === selectedConfigPanel}"
          :title="config.name" @click="$emit('select-config', name)">
        <a href="/#settings">
        <span class="icon">
          <i :class="config.icon['class']" v-if="config.icon?.['class']" />
          <img :src="config.icon?.imgUrl" v-else-if="config.icon?.imgUrl" alt="name"/>
          <i class="fas fa-puzzle-piece" v-else />
        </span>
        <span class="name" v-if="!collapsed" v-text="config.name" />
        </a>
      </li>
    </ul>

    <ul class="plugins" v-else>
      <li v-for="name in panelNames" :key="name" class="entry" :class="{selected: name === selectedPanel}"
          :title="name" @click="onItemClick(name)">
        <a :href="`/#${name}`">
        <span class="icon">
          <i :class="icons[name].class" v-if="specialPlugins.includes(name)" />
          <ExtensionIcon :name="name" size="1.5em" v-else />
        </span>
        <span class="name" v-if="!collapsed" v-text="displayName(name)" />
        </a>
      </li>
    </ul>

    <ul class="footer">
      <li :class="{selected: selectedPanel === 'extensions'}" title="Extensions" @click="onItemClick('extensions')">
        <a href="/#extensions">
          <span class="icon">
            <i class="fa fa-puzzle-piece" />
          </span>
          <span class="name" v-if="!collapsed">Extensions</span>
        </a>
      </li>

      <li :class="{selected: selectedPanel === 'settings'}" title="Settings" @click="onItemClick('settings')">
        <a href="/#settings">
          <span class="icon">
            <i class="fa fa-cog" />
          </span>
          <span class="name" v-if="!collapsed">Settings</span>
        </a>
      </li>

      <li title="Logout" @click="onItemClick('logout')">
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
import icons from '@/assets/icons.json'
import ExtensionIcon from "@/components/elements/ExtensionIcon"
import Utils from "@/Utils";
import configSections from '@/components/panels/Settings/sections.json';
import { bus } from "@/bus";

export default {
  name: "Nav",
  emits: ['select', 'select-config'],
  mixins: [Utils],
  components: {
    ExtensionIcon,
  },

  props: {
    panels: {
      type: Object,
      required: true,
    },

    selectedPanel: {
      type: String,
    },

    selectedConfigPanel: {
      type: String,
    },

    hostname: {
      type: String,
    },
  },

  computed: {
    specialPlugins() {
      return ['execute', 'entities']
    },

    panelNames() {
      const prepend = (names, name) => {
        const idx = panelNames.indexOf(name)
        if (idx >= 0)
          names = [name].concat((names.slice(0, idx).concat(names.slice(idx+1))))

        return names
      }

      let panelNames = Object.keys(this.panels).sort()
      panelNames = prepend(panelNames, 'execute')
      panelNames = prepend(panelNames, 'entities')
      return panelNames
    },

    collapsedDefault() {
      if (this.isMobile() || this.isTablet())
        return true
      return false
    },
  },

  methods: {
    onItemClick(name) {
      this.$emit('select', name)
      this.collapsed = this.isMobile() ? true : this.collapsedDefault
    },

    displayName(name) {
      if (name === 'entities')
        return 'Home'
      if (name === 'execute')
        return 'Execute'

      return name
    },

    setConnected(connected) {
      this.connected = connected
    },
  },

  data() {
    return {
      collapsed: true,
      connected: false,
      icons: icons,
      host: null,
      configSections: configSections,
    }
  },

  mounted() {
    this.collapsed = this.collapsedDefault
    bus.on('connect', () => this.setConnected(true))
    bus.on('disconnect', () => this.setConnected(false))
    this.$watch(() => this.$root.connected, (value) => this.setConnected(value))
    this.setConnected(this.$root.connected)
  },
}
</script>

<!--suppress SassScssResolvedByNameOnly -->
<style lang="scss" scoped>
$toggler-height: 2em;
$footer-collapsed-height: 7.5em;
$footer-expanded-height: 11em;

nav {
  @media screen and (max-width: #{$tablet - 1px}) {
    width: 100%;
    height: 100vh;
    background: $nav-bg;
    color: $nav-fg;
    box-shadow: $nav-box-shadow-main;

    &.collapsed {
      box-shadow: 1px 1px 1px 1px $default-shadow-color;
      margin-bottom: 2px;
      z-index: 1;
    }

    &:not(.collapsed) {
      position: absolute;
      top: 0;
      left: 0;
      z-index: 5;

      .icon.status {
        top: 0.75em !important;
        left: 2em;
      }
    }
  }

  @media screen and (min-width: $tablet) {
    width: calc(16em - 2vw);
    min-width: calc(16em - 2vw);
    height: 100%;
    overflow: auto;
    background: $nav-bg;
    color: $nav-fg;
    box-shadow: $nav-box-shadow-main;
    z-index: 1;
  }

  @media screen and (min-width: $desktop) {
    width: 20em;
    min-width: 20em;
  }

  li {
    border-bottom: $nav-entry-border;
    cursor: pointer;
    list-style: none;

    a {
      display: block;
      color: $nav-fg;
      padding: 1em 0.5em;
      text-decoration: none;

      &:hover {
        color: $nav-fg;
      }
    }

    &.selected {
      background: $nav-entry-selected-bg;
      border: 1px solid rgba(0, 0, 0, 0);
    }

    &:hover {
      background: $nav-entry-hover-bg;
      border: 1px solid rgba(0, 0, 0, 0);
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
    height: $toggler-height;
    background: $nav-toggler-bg;
    display: flex;
    font-size: 1.5em;
    position: relative;
    cursor: pointer;
    padding: 0.4em;
    align-items: center;
    box-shadow: $nav-toggler-shadow;

    .icon.status {
      position: absolute;
      top: calc($toggler-height / 2 + 0.3em);
      right: 0.5em;
      font-size: 0.5em;

      &.ok {
        color: $ok-fg;
      }

      &.error {
        color: $error-fg;
      }
    }
  }

  .hostname {
    font-size: 0.7em;
    margin-top: -0.2em;

    @media screen and (min-width: $tablet) {
      margin-left: 1em;
    }

    @media screen and (max-width: #{$tablet - 1px}) {
      text-align: right;
      margin-right: 0.25em;
      flex-grow: 1;
    }
  }

  .plugins {
    height: calc(100% - #{$toggler-height} - #{$footer-expanded-height} - 1.5em);
    overflow: auto;

    :deep(.icon) {
      display: inline-flex;

      .extension-icon {
        margin-left: 0;
        display: inline-flex;
      }
    }
  }

  .footer {
    height: calc($footer-expanded-height + 0.4em);
    background: $nav-footer-bg;
    padding: 0;
    margin: 0;

    li:last-child {
      border: 0;
    }
  }

  ul {
    li {
      .icon {
        margin-right: 0;

        & img, i {
          width: 1.5em;
          height: 1.5em;
        }
      }
    }
  }

  .icon.status {
    width: 1em;
  }

  &.collapsed {
    display: flex;
    flex-direction: column;
    margin-right: 1px;

    @media screen and (min-width: $tablet) {
      width: 2.5em;
      min-width: 2.5em;
      max-width: 2.5em;
      background: $nav-collapsed-bg;
      color: $nav-collapsed-fg;
      box-shadow: $nav-box-shadow-collapsed;

      .hostname {
        display: none;
      }
    }

    @media screen and (max-width: #{$tablet - 1px}) {
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
      box-shadow: none;
      background: $nav-toggler-collapsed-bg;

      .icon.status {
        top: 0.75em;
        left: 2em;
      }

      @include until($tablet) {
        background: $nav-toggler-collapsed-mobile-bg;
        color: $nav-toggler-collapsed-mobile-fg;

        .icon.status {
          top: 0.75em !important;
        }
      }
    }

    .footer {
      height: $footer-collapsed-height;
      background: none;
      padding: 0;
      margin-bottom: .5em;
      box-shadow: none;
    }

    @media screen and (max-width: #{$tablet - 1px}) {
      .footer {
        display: none;
      }
    }

    ul {
      display: flex;
      flex-direction: column;
      justify-content: center;
      height: calc(100% - #{$toggler-height} - #{$footer-collapsed-height});
      overflow: hidden;

      &.plugins {
        @media screen and (min-width: $tablet) and (max-width: #{$desktop - 1px}) {
          margin: 2em 0;
        }
      }

      &:hover {
        overflow: auto;
      }

      li {
        border: none;
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

        @media screen and (max-width: #{$tablet - 1px}) {
          display: none;
        }
      }
    }
  }
}
</style>

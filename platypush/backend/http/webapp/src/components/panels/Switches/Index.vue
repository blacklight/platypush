<template>
  <div class="switches-container">
    <Loading v-if="loading" />

    <div class="switch-plugins">
      <div class="no-content" v-if="!Object.keys(plugins).length">No switch plugins configured</div>

      <div class="switch-plugin" v-for="pluginName in Object.keys(plugins)" :key="pluginName"
           @click="selectedPlugin = selectedPlugin === pluginName ? null : pluginName">
        <div class="header" :class="{selected: selectedPlugin === pluginName}">
          <div class="name col-10" v-text="pluginName" />
          <div class="refresh col-2" v-if="selectedPlugin === pluginName">
            <button @click.stop="bus.emit('refresh', pluginName)" title="Refresh plugin" :disabled="loading">
              <i class="fa fa-sync" />
            </button>
          </div>
        </div>

        <div class="body" :class="{hidden: selectedPlugin !== pluginName}">
          <component :is="components[pluginName]" :config="plugins[pluginName]" :plugin-name="pluginName"
                     :selected="selectedPlugin === pluginName" :bus="bus" />
        </div>
      </div>
    </div>

    <div class="refresh-button">
      <button @click="refresh" :disabled="loading" title="Refresh plugins">
        <i class="fa fa-sync" />
      </button>
    </div>
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import Utils from "@/Utils";
import {defineAsyncComponent} from "vue";
import mitt from "mitt";

export default {
  name: "Switches",
  components: {Loading},
  mixins: [Utils],

  data() {
    return {
      loading: false,
      plugins: {},
      components: {},
      selectedPlugin: null,
      bus: mitt(),
    }
  },

  methods: {
    initPanels() {
      this.components = {}

      Object.keys(this.plugins).forEach(async (pluginName) => {
        const componentName = pluginName.split('.').map((token) => token[0].toUpperCase() + token.slice(1)).join('')
        let comp = null
        try {
          comp = await import(`@/components/panels/Switches/${componentName}/Index`)
        } catch (e) {
          return
        }

        const component = defineAsyncComponent(async () => { return comp })
        this.$options.components[pluginName] = component
        this.components[pluginName] = component
      })
    },

    async refresh() {
      this.loading = true

      try {
        this.plugins = await this.request('utils.get_switch_plugins')
        this.initPanels()
      } finally {
        this.loading = false
      }
    },
  },

  mounted() {
    this.refresh()
  },
}
</script>

<style lang="scss" scoped>
@import "vars";

.switches-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: auto;

  .switch-plugins {
    background: $background-color;
    display: flex;
    flex-direction: column;
    box-shadow: $border-shadow-bottom-right;

    @media screen and (max-width: calc(#{$tablet - 1px})) {
      width: 100%;
    }

    @media screen and (min-width: $tablet) {
      width: 90%;
      border-radius: 1em;
      margin-top: 2em;
    }

    @media screen and (min-width: $desktop) {
      width: 500pt;
      margin-top: 3em;
    }
  }

  .no-content {
    padding: 1.5em;
  }

  .switch-plugin {
    display: flex;
    flex-direction: column;

    .header {
      display: flex;
      align-items: center;
      padding: 1em 1.5em 1em .5em;
      text-transform: uppercase;
      letter-spacing: .075em;
      border-bottom: $default-border-2;
      cursor: pointer;

      &:hover {
        background: $hover-bg;
      }

      &.selected {
        background: $selected-bg;
        box-shadow: $border-shadow-bottom-right;
        border: none;
      }

      .refresh {
        text-align: right;
      }

      button {
        padding: 0;
        margin: 0;
        border: none;
        background: none;

        &:hover {
          color: $default-hover-fg-2;
        }
      }
    }

    @media screen and (min-width: $tablet) {
      &:first-child {
        .header {
          border-radius: 1em 1em 0 0;
        }
      }

      &:last-child {
        .header {
          border-radius: 0 0 1em 1em;
        }
      }
    }

    .body {
      display: flex;
      border: $default-border-2;
      border-bottom: 0;
      box-shadow: $border-shadow-bottom;
    }
  }

  .refresh-button {
    position: fixed;
    bottom: 1.5em;
    right: 1.5em;

    button {
      width: 4em;
      height: 4em;
      border-radius: 2em;
      background: $refresh-button-bg;
      color: $refresh-button-fg;
      border: none;
      box-shadow: $border-shadow-bottom-right;

      &:hover {
        color: $default-hover-fg-2;
      }

      &:disabled {
        opacity: .7;
      }
    }
  }
}
</style>

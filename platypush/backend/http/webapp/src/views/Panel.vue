<template>
  <main>
    <Loading v-if="loading" />
    <Nav :panels="components"
         :selected-panel="selectedPanel"
         :selected-config-panel="selectedConfigPanel"
         :hostname="hostname"
         @select="selectedPanel = $event"
         @select-config="selectedConfigPanel = $event"
         v-else
    />

    <div class="canvas" v-if="selectedPanel === 'settings'">
      <div class="panel">
        <Settings :selected-panel="selectedConfigPanel" />
      </div>
    </div>

    <div class="canvas" v-else-if="selectedPanel === 'extensions'">
      <div class="panel">
        <Extensions />
      </div>
    </div>

    <div class="canvas" v-else>
      <div class="panel" :class="{hidden: name !== selectedPanel}" v-for="(panel, name) in components" :key="name">
        <component :is="panel.component" :config="panel.config" :plugin-name="name" v-if="name === selectedPanel" />
      </div>
    </div>
  </main>
</template>

<script>
import { defineAsyncComponent, shallowRef } from "vue";
import Utils from '@/Utils'
import Loading from "@/components/Loading";
import Nav from "@/components/Nav";
import Extensions from "@/components/panels/Extensions/Index";
import Settings from "@/components/panels/Settings/Index";

export default {
  name: 'Panel',
  mixins: [Utils],
  components: {Extensions, Settings, Nav, Loading},

  data() {
    return {
      loading: false,
      plugins: {},
      backends: {},
      procedures: {},
      components: {},
      hostname: undefined,
      selectedPanel: undefined,
      selectedConfigPanel: 'users',
    }
  },

  methods: {
    initSelectedPanel() {
      const match = this.$route.hash.match(/^#?([a-zA-Z0-9_.]+)(\?(.+?))?/)
      const plugin = match ? match[1] : 'entities'
      if (plugin?.length)
        this.selectedPanel = plugin
    },

    initPanels() {
      const self = this
      this.components = {}

      Object.entries(this.plugins).forEach(async ([name, plugin]) => {
        const componentName = name.split('.').map((token) => token[0].toUpperCase() + token.slice(1)).join('')
        let comp = null
        try {
          comp = await import(`@/components/panels/${componentName}/Index`)
        } catch (e) {
          return
        }

        const component = shallowRef(defineAsyncComponent(async () => { return comp }))
        self.$options.components[name] = component
        self.components[name] = {
          component: component,
          pluginName: name,
          config: plugin,
        }
      })
    },

    async parseConfig() {
      [this.plugins, this.backends, this.procedures, this.hostname] =
          await Promise.all([
            this.request('config.get_plugins'),
            this.request('config.get_backends'),
            this.request('config.get_procedures'),
            this.request('config.get_device_id'),
          ])

      this.initializeDefaultViews()
    },

    initializeDefaultViews() {
      this.plugins.entities = {}
      this.plugins.execute = {}
    },
  },

  async mounted() {
    this.loading = true

    try {
      await this.parseConfig()
      this.initPanels()
      this.initSelectedPanel()
      this.$watch('$route.hash', this.initSelectedPanel)
    } finally {
      this.loading = false
    }
  },
}
</script>

<style lang="scss" scoped>
main {
  height: 100%;
  display: flex;

  @include until($tablet) {
    flex-direction: column;
  }

  .canvas {
    display: flex;
    flex-grow: 100;
    background: $menu-panel-bg;
    overflow: auto;
    z-index: 1;

    .panel {
      width: 100%;
      height: 100%;
      display: flex;
      margin: 0 !important;
      box-shadow: none !important;
      overflow: auto;
    }
  }
}
</style>

<style>
html {
  overflow: auto !important;
}
</style>

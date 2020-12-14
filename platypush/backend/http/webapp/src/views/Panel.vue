<template>
  <main>
    <Loading v-if="loading" />
    <Nav :panels="components" :selected-panel="selectedPanel" :hostname="hostname"
         @select="selectedPanel = $event" v-else />

    <div class="canvas">
      <div class="panel" v-for="(panel, name) in components" :key="name">
        <component :is="panel.component" :config="panel.config" :plugin-name="name" v-if="name === selectedPanel" />
      </div>
    </div>
  </main>
</template>

<script>
import {defineAsyncComponent} from "vue";
import Utils from '@/Utils'
import Loading from "@/components/Loading";
import Nav from "@/components/Nav";

export default {
  name: 'Panel',
  mixins: [Utils],
  components: {Nav, Loading},

  data() {
    return {
      loading: false,
      plugins: {},
      backends: {},
      procedures: {},
      components: {},
      hostname: undefined,
      selectedPanel: undefined,
    }
  },

  methods: {
    initSelectedPanel() {
      const match = this.$route.hash.match('#?([a-zA-Z0-9.]+)[?]?(.*)')
      if (!match)
        return

      const plugin = match[1]
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

        const component = defineAsyncComponent(async () => { return comp })
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
    },
  },

  async mounted() {
    this.loading = true

    try {
      await this.parseConfig()
      this.initPanels()
      this.initSelectedPanel()
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

  @media screen and (max-width: $tablet) {
    flex-direction: column;
  }

  .canvas {
    display: flex;
    flex-grow: 100;
    background: $menu-panel-bg;
    overflow: auto;

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

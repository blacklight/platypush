<template>
  <main>
    <Loading v-if="loading" />
    <div class="canvas" v-else>
      <component :is="component" :config="config" :plugin-name="pluginName" />
    </div>
  </main>
</template>

<script>
import {defineAsyncComponent} from "vue";
import Utils from '@/Utils'
import Loading from "@/components/Loading";
import Nav from "@/components/Nav";
import Settings from "@/components/panels/Settings/Index";

export default {
  name: 'Panel',
  mixins: [Utils],
  components: {Settings, Nav, Loading},

  data() {
    return {
      loading: false,
      config: {},
      plugins: {},
      backends: {},
      procedures: {},
      component: undefined,
      hostname: undefined,
      selectedPanel: undefined,
    }
  },

  computed: {
    pluginName() {
      return this.$route.params.plugin
    },
  },

  methods: {
    async initPanel() {
      const componentName = this.pluginName.split('.').map((token) => token[0].toUpperCase() + token.slice(1)).join('')
      let comp = null

      try {
        comp = await import(`@/components/panels/${componentName}/Index`)
      } catch (e) {
        console.error(e)
        this.notify({
          error: true,
          title: `Cannot load plugin ${this.pluginName}`,
          text: e.toString(),
        })

        return
      }

      this.component = defineAsyncComponent(async () => { return comp })
      this.$options.components[name] = this.component
    },

    async initConfig() {
      const config = await this.request('config.get')
      this.config = config[this.pluginName] || {}
      this.hostname = await this.request('config.get_device_id')
    },
  },

  async mounted() {
    this.loading = true

    try {
      await this.initConfig()
      await this.initPanel()
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

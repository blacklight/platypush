<template>
  <div class="plugin">
    <Loading v-if="loading" />
    <component :is="component" :config="config" v-else-if="component" />
  </div>
</template>

<script>
import Utils from "@/Utils";
import Loading from "@/components/Loading";
import { defineAsyncComponent, shallowRef } from "vue";

export default {
  name: "Plugin",
  components: {Loading},
  mixins: [Utils],
  props: {
    // Name of the plugin view to be loaded
    pluginName: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      loading: false,
      component: null,
      config: {},
    }
  },

  computed: {
    componentName() {
      return this.pluginName.split('.').map((t) => t[0].toUpperCase() + t.slice(1)).join('')
    },
  },

  methods: {
    refresh: async function() {
      this.loading = true

      try {
        this.component = shallowRef(defineAsyncComponent(() => import(`@/components/panels/${this.componentName}/Index`)))
        this.$options.components[this.componentName] = this.component
        this.config = (await this.request('config.get_plugins'))?.[this.pluginName] || {}
      } finally {
        this.loading = false
      }
    },
  },

  mounted: function() {
    this.refresh()
  },
}
</script>

<style lang="scss" scoped>
.plugin {
  margin: -1em 0 0 -1em !important;
  padding: 0;
  width: calc(100% + 2em);
  height: calc(100% + 2em);
}
</style>

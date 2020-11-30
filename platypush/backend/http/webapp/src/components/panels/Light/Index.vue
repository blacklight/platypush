<template>
  <div class="light-plugin">
    I'm in the content!
    {{ pluginName }}
  </div>
</template>

<script>
import Utils from "@/Utils";
import Panel from "@/components/panels/Panel";

/**
 * Generic component for light plugins panels.
 */
export default {
  name: "Light",
  mixins: [Utils, Panel],

  props: {
    // Set to false if the light plugin doesn't support groups.
    hasGroups: {
      type: Boolean,
      default: true,
    },

    // Set to false if the light plugin doesn't support scenes.
    hasScenes: {
      type: Boolean,
      default: true,
    },

    // Set to false if the light plugin doesn't support animations.
    hasAnimations: {
      type: Boolean,
      default: true,
    },
  },

  data() {
    return {
      lights: {},
      groups: {},
      scenes: {},
    }
  },

  methods: {
    async getLights() {
      throw "getLights should be implemented by a derived component"
    },

    async getGroups() {
      if (!this.hasGroups)
        return {}

      throw "getGroups should be implemented by a derived component"
    },

    async getScenes() {
      if (!this.hasScenes)
        return {}

      throw "getScenes should be implemented by a derived component"
    },
  },

  async mounted() {
    [this.lights, this.groups, this.scenes] = await Promise.all([
      this.getLights(),
      this.getGroups(),
      this.getScenes(),
    ])
  },
}
</script>

<style scoped>
</style>

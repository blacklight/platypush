<template>
  <div />
</template>

<script>
import Mixin from "@/components/panels/Media/Players/Mixin";

export default {
  name: "Kodi",
  mixins: [Mixin],
  data() {
    return {
      iconClass: 'fa fa-kodi',
      name: 'Kodi',
      pluginName: 'media.kodi',
    }
  },

  methods: {
    async getPlayers() {
      return [{
        iconClass: this.iconClass,
        pluginName: this.pluginName,
        name: this.$root.config['media.kodi']?.host || this.name,
        component: this,
        status: await this.request(`${this.pluginName}.status`)
      }]
    },

    supports(resource) {
      return resource?.type === 'youtube' || (resource.url || resource).startsWith('http://') ||
          (resource.url || resource).startsWith('https://')
    },
  },
}
</script>

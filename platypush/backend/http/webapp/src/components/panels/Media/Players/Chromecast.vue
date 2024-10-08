<template>
  <div />
</template>

<script>
import Mixin from "@/components/panels/Media/Players/Mixin";

export default {
  name: "Chromecast",
  mixins: [Mixin],
  emits: ['status'],
  data() {
    return {
      name: 'Chromecast',
      pluginName: 'media.chromecast',
      iconClass: 'fab fa-chromecast',
    }
  },

  methods: {
    async getPlayers() {
      const devices = Object.values(
        await this.request(`${this.pluginName}.status`)
      )

      return Promise.all(devices.map(async (device) => {
        return {
          ...device,
          iconClass: device.type === 'audio' ? 'fa fa-volume-up' : 'fab fa-chromecast',
          pluginName: this.pluginName,
          component: this,
        }
      }))
    },

    getPlayerName(player) {
      if (typeof player === 'string')
        return player

      if (!player)
        return this.player?.name

      return player?.name
    },

    async status(player) {
      return (
        await this.request(`${this.pluginName}.status`, {chromecast: this.getPlayerName(player)})
      )?.status
    },

    async play(resource, subs, player) {
      if (!resource) {
        return await this.pause(player)
      }

      return await this.request(
        `${this.pluginName}.play`,
        {
          resource: resource.url,
          chromecast: this.getPlayerName(player),
          subtitles: subs,
          metadata: resource,
        }
      )
    },

    async pause(player) {
      return await this.request(`${this.pluginName}.pause`, {chromecast: this.getPlayerName(player)})
    },

    async stop(player) {
      return await this.request(`${this.pluginName}.quit`, {chromecast: this.getPlayerName(player)})
    },

    async setVolume(volume, player) {
      return await this.request(`${this.pluginName}.set_volume`, {volume: volume, chromecast: this.getPlayerName(player)})
    },

    async seek(position, player) {
      return await this.request(`${this.pluginName}.seek`, {position: position, chromecast: this.getPlayerName(player)})
    },

    async onMediaEvent(event) {
      if (event.plugin !== this.pluginName)
        return false

      this.$emit('status', await this.status(event.player))
      return true
    },

    supports() {
      return true
    },
  },
}
</script>

<template>
  <div class="plugins">
    <Chromecast :player="selectedPlayer?.pluginName === 'media.chromecast' ? selectedPlayer : null"
                ref="chromecastPlugin" @status="$emit('status', $event)" />
    <Kodi :player="selectedPlayer?.pluginName === 'media.kodi' ? selectedPlayer : null" ref="kodiPlugin"
           @status="$emit('status', $event)" />
    <Mplayer :player="selectedPlayer?.pluginName === 'media.mplayer' ? selectedPlayer : null" ref="mplayerPlugin"
              @status="$emit('status', $event)" />
    <Mpv :player="selectedPlayer?.pluginName === 'media.mpv' ? selectedPlayer : null" ref="mpvPlugin"
         @status="$emit('status', $event)" />
    <Omxplayer :player="selectedPlayer?.pluginName === 'media.omxplayer' ? selectedPlayer : null" ref="omxplayerPlugin"
               @status="$emit('status', $event)" />
    <Vlc :player="selectedPlayer?.pluginName === 'media.vlc' ? selectedPlayer : null" ref="vlcPlugin"
         @status="$emit('status', $event)" />
  </div>

  <div class="players">
    <Dropdown :title="selectedPlayer?.name || 'Players'"
              :icon-class="selectedPlayer ? selectedPlayer.iconClass : 'fab fa-chromecast'">
      <Loading v-if="loading" />

      <div class="refresh">
        <DropdownItem text="Refresh" icon-class="fa fa-sync-alt" @click="refresh" />
      </div>

      <div class="no-results" v-if="!players?.length">No players found</div>

      <div class="player" v-for="(player, i) in players" :key="i"
           :class="{selected: selectedPlayer != null && selectedPlayer.pluginName === player.pluginName
           && selectedPlayer.name === player.name}">
        <DropdownItem :text="player.name" :icon-class="player.iconClass" @click="select(player)" />
      </div>
    </Dropdown>
  </div>
</template>

<script>
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";
import Loading from "@/components/Loading";

import Chromecast from "@/components/panels/Media/Players/Chromecast"
import Kodi from "@/components/panels/Media/Players/Kodi";
import Mplayer from "@/components/panels/Media/Players/Mplayer";
import Mpv from "@/components/panels/Media/Players/Mpv";
import Omxplayer from "@/components/panels/Media/Players/Omxplayer";
import Vlc from "@/components/panels/Media/Players/Vlc";

export default {
  name: "Players",
  components: {Loading, DropdownItem, Dropdown, Chromecast, Kodi, Mplayer, Mpv, Omxplayer, Vlc},
  emits: ['select', 'status'],

  props: {
    pluginName: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      loading: false,
      players: [],
      selectedPlayer: null,
      config: {},
      plugins: [],
    }
  },

  methods: {
    loadPlugins() {
      this.plugins = Object.entries(this.$refs).filter((p) => p[0].endsWith('Plugin')).map((p) => p[1])
    },

    async refresh() {
      this.players = []
      this.loading = true
      const config = this.$root.config

      try {
        await Promise.all(this.plugins.map(async (plugin) => {
          if (!(plugin.pluginName in config))
            return

          const players = await plugin.getPlayers()
          this.players.push(...players)

          if (this.selectedPlayer == null && plugin.pluginName === this.pluginName && players.length > 0) {
            this.select(players[0])
          }
        }))
      } finally {
        this.loading = false
      }
    },

    select(player) {
      this.selectedPlayer = player
      this.$emit('select', player)
    },
  },

  async mounted() {
    await this.loadPlugins()
    await this.refresh()
  }
}
</script>

<style lang="scss" scoped>
.plugins {
  display: none;
}

.no-results {
  padding: 1em;
}

.players {
  :deep(.dropdown) {
    direction: ltr;
    .item {
      padding: .5em;
    }

    .icon {
      margin-right: 1em !important;
    }
  }

  :deep(.refresh) {
    font-weight: bold;
    font-size: .8em;
    opacity: .7;
  }

  :deep(.player.selected) {
    color: $selected-fg;
  }
}
</style>

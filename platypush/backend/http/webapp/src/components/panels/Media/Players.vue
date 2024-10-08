<template>
  <div class="media-players">
    <div class="plugins">
      <Chromecast :player="selectedPlayer?.pluginName === 'media.chromecast' ? selectedPlayer : null"
                  ref="chromecastPlugin" @status="$emit('status', $event)" />
      <Kodi :player="selectedPlayer?.pluginName === 'media.kodi' ? selectedPlayer : null" ref="kodiPlugin"
             @status="$emit('status', $event)" />
      <Mplayer :player="selectedPlayer?.pluginName === 'media.mplayer' ? selectedPlayer : null" ref="mplayerPlugin"
                @status="$emit('status', $event)" />
      <Mpv :player="selectedPlayer?.pluginName === 'media.mpv' ? selectedPlayer : null" ref="mpvPlugin"
           @status="$emit('status', $event)" />
      <GStreamer :player="selectedPlayer?.pluginName === 'media.gstreamer' ? selectedPlayer : null"
                 ref="gstreamerPlugin" @status="$emit('status', $event)" />
      <Vlc :player="selectedPlayer?.pluginName === 'media.vlc' ? selectedPlayer : null" ref="vlcPlugin"
           @status="$emit('status', $event)" />
    </div>

    <div class="players">
      <Dropdown :title="selectedPlayer?.name || 'Players'"
                :icon-class="selectedPlayer ? selectedPlayer.iconClass : 'fab fa-chromecast'">
        <Loading v-if="loading" />

        <div class="refresh">
          <DropdownItem text="Refresh" icon-class="fa fa-sync-alt" @input="refresh" />
        </div>

        <div class="no-results" v-if="!players?.length">No players found</div>

        <div class="player" v-for="(player, i) in players" :key="i"
             :class="{selected: selectedPlayer != null && selectedPlayer.pluginName === player.pluginName
             && selectedPlayer.name === player.name}">
          <DropdownItem :text="player.name" :icon-class="player.iconClass" @input="select(player)" />
        </div>
      </Dropdown>
    </div>
  </div>
</template>

<script>
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";
import Loading from "@/components/Loading";
import Utils from '@/Utils'

import Chromecast from "@/components/panels/Media/Players/Chromecast"
import Kodi from "@/components/panels/Media/Players/Kodi";
import Mplayer from "@/components/panels/Media/Players/Mplayer";
import Mpv from "@/components/panels/Media/Players/Mpv";
import GStreamer from "@/components/panels/Media/Players/GStreamer";
import Vlc from "@/components/panels/Media/Players/Vlc";

export default {
  name: "Players",
  components: {Loading, DropdownItem, Dropdown, Chromecast, Kodi, Mplayer, Mpv, GStreamer, Vlc},
  emits: ['select', 'status'],
  mixins: [Utils],

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
            const urlSelectedPlayer = this.getUrlArgs().player
            let player = players[0]

            if (urlSelectedPlayer?.length) {
              player = players.find((p) => p.name === urlSelectedPlayer)
              if (!player)
                player = players[0]
            }

            this.select(player)
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

<style lang="scss">
.media-players {
  .plugins {
    display: none;
  }

  .no-results {
    padding: 1em;
  }
}

.dropdown-container {
  .refresh {
    font-weight: bold;
    font-size: .8em;
    opacity: .7;
  }

  .player.selected {
    .item {
      color: $selected-fg;
    }
  }
}
</style>

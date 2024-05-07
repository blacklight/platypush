<template>
  <keep-alive>
    <div class="media-plugin fade-in">
      <Loading v-if="loading" />

      <MediaView :plugin-name="pluginName" :status="selectedPlayer?.status || {}" :track="selectedPlayer?.status || {}"
                 :buttons="mediaButtons" @play="pause" @pause="pause" @stop="stop" @set-volume="setVolume"
                 @seek="seek" @search="search" @mute="toggleMute" @unmute="toggleMute">
        <main>
          <div class="nav-container from tablet" :style="navContainerStyle">
            <Nav :selected-view="selectedView"
                 :torrent-plugin="torrentPlugin"
                 @input="selectedView = $event"
                 @toggle="forceShowNav = !forceShowNav" />
          </div>

          <div class="view-container">
            <Header :plugin-name="pluginName"
                    :selected-view="selectedView"
                    :has-subtitles-plugin="hasSubtitlesPlugin"
                    :sources="sources"
                    :selected-item="selectedItem"
                    :selected-subtitles="selectedSubtitles"
                    :browser-filter="browserFilter"
                    :show-nav-button="!forceShowNav"
                    ref="header"
                    @search="search"
                    @select-player="selectedPlayer = $event"
                    @player-status="onStatusUpdate"
                    @torrent-add="downloadTorrent($event)"
                    @show-subtitles="showSubtitlesModal = !showSubtitlesModal"
                    @play-url="showPlayUrlModal"
                    @filter="browserFilter = $event"
                    @toggle-nav="forceShowNav = !forceShowNav"
                    @source-toggle="sources[$event] = !sources[$event]" />

            <div class="body-container" :class="{'expanded-header': $refs.header?.filterVisible}">
              <Results :results="results"
                       :selected-result="selectedResult"
                       :sources="sources"
                       :loading="loading"
                       :filter="browserFilter"
                       @select="onResultSelect($event)"
                       @play="play"
                       @view="view"
                       @download="download"
                       v-if="selectedView === 'search'" />

              <TorrentView :plugin-name="torrentPlugin"
                           :is-media="true"
                           @play="play"
                           v-else-if="selectedView === 'torrents'" />

              <Browser :filter="browserFilter"
                       @path-change="browserFilter = ''"
                       @play="play($event)"
                       v-else-if="selectedView === 'browser'" />
            </div>
          </div>
        </main>
      </MediaView>

      <div class="subtitles-container">
        <Modal title="Available subtitles" :visible="showSubtitlesModal" ref="subtitlesSelector"
               @close="showSubtitlesModal = false">
          <div class="subtitles-content" v-if="showSubtitlesModal && selectedResult != null" >
            <Subtitles :item="selectedPlayer && selectedPlayer.status &&
              (selectedPlayer.status.state === 'play' || selectedPlayer.status.state === 'pause')
              ? selectedPlayer.status : results[selectedResult]" @select-subs="selectSubtitles($event)" />
          </div>
        </Modal>
      </div>

      <div class="play-url-container">
        <Modal title="Play URL" ref="playUrlModal" @open="onPlayUrlModalOpen">
          <UrlPlayer :value="urlPlay" @input="urlPlay = $event.target.value" @play="playUrl($event)" />
        </Modal>
      </div>
    </div>
  </keep-alive>
</template>

<script>
import Loading from "@/components/Loading";
import Modal from "@/components/Modal";
import Utils from "@/Utils";

import Browser from "@/components/panels/Media/Browser";
import Header from "@/components/panels/Media/Header";
import MediaUtils from "@/components/Media/Utils";
import MediaView from "@/components/Media/View";
import Nav from "@/components/panels/Media/Nav";
import Results from "@/components/panels/Media/Results";
import Subtitles from "@/components/panels/Media/Subtitles";
import TorrentView from "@/components/panels/Torrent/View";
import UrlPlayer from "@/components/panels/Media/UrlPlayer";

export default {
  name: "Media",
  mixins: [Utils, MediaUtils],
  components: {
    Browser,
    Header,
    Loading,
    MediaView,
    Modal,
    Nav,
    Results,
    Subtitles,
    TorrentView,
    UrlPlayer,
  },

  props: {
    pluginName: {
      type: String,
      required: true,
    },

    mediaButtons: {
      type: Object,
      default: () => {
        return {
          previous: false,
          next: false,
          stop: true,
        }
      }
    }
  },

  data() {
    return {
      loading: false,
      results: [],
      selectedResult: null,
      selectedPlayer: null,
      selectedView: 'search',
      selectedSubtitles: null,
      showSubtitlesModal: false,
      forceShowNav: false,
      awaitingPlayTorrent: null,
      urlPlay: null,
      browserFilter: null,
      torrentPlugin: null,
      torrentPlugins: [
        'torrent',
        'rtorrent',
      ],

      sources: {
        'file': true,
        'youtube': true,
        'torrent': true,
      },
    }
  },

  computed: {
    hasSubtitlesPlugin() {
      return 'media.subtitles' in this.$root.config
    },

    navContainerStyle() {
      if (this.forceShowNav)
        return {
          display: 'flex !important',
        }

      return {}
    },

    selectedItem() {
      if (
        this.selectedPlayer && this.selectedPlayer.status &&
        (
          this.selectedPlayer.status.state === 'play' ||
          this.selectedPlayer.status.state === 'pause'
        )
      )
        return this.selectedPlayer.status

      return this.results[this.selectedResult]
    },
  },

  methods: {
    async search(event) {
      this.loading = true

      try {
        this.results = await this.request(`${this.pluginName}.search`, event)
      } finally {
        this.loading = false
      }
    },

    async play(item) {
      if (item?.type === 'torrent') {
        this.awaitingPlayTorrent = item.url
        this.notify({
          text: 'Torrent queued for download',
          image: {
            iconClass: 'fa fa-magnet',
          }
        })

        await this.download(item)
        return
      }

      this.loading = true

      try {
        if (!this.selectedPlayer.component.supports(item))
          item = await this.startStreaming(item, this.pluginName)

        await this.selectedPlayer.component.play(item, this.selectedSubtitles, this.selectedPlayer)
        await this.refresh()
      } finally {
        this.loading = false
      }
    },

    async pause() {
      await this.selectedPlayer.component.pause(this.selectedPlayer)
      await this.refresh()
    },

    async stop() {
      await this.selectedPlayer.component.stop(this.selectedPlayer)
      await this.refresh()
    },

    async setVolume(volume) {
      await this.selectedPlayer.component.setVolume(volume, this.selectedPlayer)
      await this.refresh()
    },

    async toggleMute() {
      await this.selectedPlayer.component.toggleMute(this.selectedPlayer)
      await this.refresh()
    },

    async seek(position) {
      await this.selectedPlayer.component.seek(position, this.selectedPlayer)
      await this.refresh()
    },

    async view(item) {
      const ret = await this.startStreaming(item, this.pluginName, true)
      window.open(ret.url, '_blank')
    },

    async download(item) {
      if (item?.type === 'torrent') {
        await this.downloadTorrent(item)
      }
    },

    async refresh() {
      this.selectedPlayer.status = await this.selectedPlayer.component.status(this.selectedPlayer)
    },

    onStatusUpdate(status) {
      if (!this.selectedPlayer)
        return

      this.selectedPlayer.status = status
    },

    onPlayUrlModalOpen() {
      const modal = this.$refs.playUrlModal
      this.urlPlay = ''
      modal.$nextTick(() => {
        const input = modal.$el.querySelector('input[type=text]')
        if (input) {
          input.focus()
          input.select()
        }
      })
    },

    onTorrentQueued(event) {
      this.notify({
        title: 'Torrent queued for download',
        text: event.name,
        image: {
          iconClass: 'fa fa-magnet',
        }
      })
    },

    onTorrentMetadata(event) {
      this.notify({
        title: 'Torrent metadata downloaded',
        text: event.name,
        image: {
          iconClass: 'fa fa-info',
        }
      })
    },

    onTorrentDownloadStart(event) {
      this.notify({
        title: 'Torrent download started',
        text: event.name,
        image: {
          iconClass: 'fa fa-download',
        }
      })
    },

    onTorrentDownloadCompleted(event) {
      this.notify({
        title: 'Torrent download completed',
        text: event.name,
        image: {
          iconClass: 'fa fa-check',
        }
      })
    },

    getTorrentPlugin() {
      const pluginConf = this.$root.config[this.pluginName] || {}
      let torrentPlugin = pluginConf.torrent_plugin
      if (!torrentPlugin) {
        for (let plugin of this.torrentPlugins) {
          if (plugin in this.$root.config) {
            torrentPlugin = plugin
            break
          }
        }
      }

      return torrentPlugin
    },

    async downloadTorrent(item) {
      const torrentPlugin = this.getTorrentPlugin()
      if (!torrentPlugin) {
        this.notify({
          text: 'No torrent plugins configured',
          error: true,
        })

        return
      }

      return await this.request(`${torrentPlugin}.download`, {torrent: item?.url || item})
    },

    async selectSubtitles(item) {
      this.$refs.subtitlesSelector.close()
      if (!item) {
        this.selectedSubtitles = null
        return
      }

      this.notify({
        text: 'Downloading subtitles track',
        image: {
          iconClass: 'fa fa-download',
        }
      })

      const subs = await this.request('media.subtitles.download', {link: item.SubDownloadLink})
      this.selectedSubtitles = subs.filename

      this.notify({
        text: 'Subtitles track downloaded',
        image: {
          iconClass: 'fa fa-check',
        }
      })
    },

    onResultSelect(result) {
      if (this.selectedResult == null || this.selectedResult !== result) {
        this.selectedResult = result
        this.selectedSubtitles = null
      } else {
        this.selectedResult = null
      }
    },

    showPlayUrlModal() {
      this.$refs.playUrlModal.show()
    },

    async playUrl(url) {
      this.urlPlay = url
      this.loading = true

      try {
        await this.play({
          url: url,
        })

        this.$refs.playUrlModal.close()
      } finally {
        this.loading = false
      }
    },
  },

  mounted() {
    this.$watch(() => this.selectedPlayer, (player) => {
      if (player)
        this.refresh()
    })

    this.$watch(() => this.selectedSubtitles, (subs) => {
      if (new Set(['play', 'pause']).has(this.selectedPlayer?.status?.state)) {
        if (subs)
          this.selectedPlayer.component.addSubtitles(subs)
        else
          this.selectedPlayer.component.removeSubtitles()
      }
    })

    this.torrentPlugin = this.getTorrentPlugin()
    this.subscribe(this.onTorrentQueued,'notify-on-torrent-queued',
        'platypush.message.event.torrent.TorrentQueuedEvent')
    this.subscribe(this.onTorrentMetadata,'on-torrent-metadata',
        'platypush.message.event.torrent.TorrentDownloadedMetadataEvent')
    this.subscribe(this.onTorrentDownloadStart,'notify-on-torrent-download-start',
        'platypush.message.event.torrent.TorrentDownloadStartEvent')
    this.subscribe(this.onTorrentDownloadCompleted,'notify-on-torrent-download-completed',
        'platypush.message.event.torrent.TorrentDownloadCompletedEvent')

    if ('media.plex' in this.$root.config)
      this.sources.plex = true

    if ('media.jellyfin' in this.$root.config)
      this.sources.jellyfin = true
  },

  destroy() {
    this.unsubscribe('notify-on-torrent-queued')
    this.unsubscribe('on-torrent-metadata')
    this.unsubscribe('notify-on-torrent-download-start')
    this.unsubscribe('notify-on-torrent-download-completed')
  },
}
</script>

<style lang="scss" scoped>
@import "~@/components/Media/vars";

.media-plugin {
  width: 100%;

  main {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: row-reverse;

    .view-container {
      display: flex;
      flex-direction: column;
      flex-grow: 1;
      overflow: auto;
      background: $background-color;
    }

    .body-container {
      height: calc(100% - #{$media-header-height} - #{$media-ctrl-panel-height});
      padding-top: .1em;
      overflow: auto;

      &.expanded-header {
        height: calc(100% - #{$media-header-height} - #{$filter-header-height} - #{$media-ctrl-panel-height});
      }
    }
  }
}

:deep(.loading) {
  z-index: 10;
}

:deep(.subtitles-container) {
  .body {
    padding: 0 !important;

    .item {
      padding: 1em;
    }
  }
}
</style>

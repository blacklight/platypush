<template>
  <keep-alive>
    <div class="media-plugin fade-in">
      <Loading v-if="loading" />

      <MediaView :plugin-name="pluginName" :status="selectedPlayer?.status || {}" :track="selectedPlayer?.status || {}"
                 :buttons="mediaButtons" @play="pause" @pause="pause" @stop="stop" @set-volume="setVolume"
                 @seek="seek" @search="search">
        <main>
          <div class="nav-container">
            <Nav :selected-view="selectedView" @input="selectedView = $event" />
          </div>

          <div class="view-container">
            <Header :plugin-name="pluginName" :selected-view="selectedView" :has-subtitles-plugin="hasSubtitlesPlugin"
                    :selected-item="selectedPlayer && selectedPlayer.status &&
                      (selectedPlayer.status.state === 'play' || selectedPlayer.status.state === 'pause')
                      ? selectedPlayer.status : results[selectedResult]" :selected-subtitles="selectedSubtitles"
                    @search="search" @select-player="selectedPlayer = $event" @player-status="onStatusUpdate"
                    @torrent-add="downloadTorrent($event)" @show-subtitles="showSubtitlesModal = !showSubtitlesModal" />

            <div class="body-container">
              <Results :results="results" :selected-result="selectedResult" @select="onResultSelect($event)"
                       @play="play" @info="$refs.mediaInfo.isVisible = true" @view="view" @download="download"
                       v-if="selectedView === 'search'" />

              <TorrentView :plugin-name="torrentPlugin" :is-media="true" @play="play"
                           v-else-if="selectedView === 'torrents'" />
            </div>
          </div>
        </main>
      </MediaView>

      <div class="media-info-container">
        <Modal title="Media info" ref="mediaInfo">
          <Info :item="results[selectedResult]" v-if="selectedResult != null" />
        </Modal>
      </div>

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
    </div>
  </keep-alive>
</template>

<script>
import Loading from "@/components/Loading";
import Modal from "@/components/Modal";
import Utils from "@/Utils";
import MediaUtils from "@/components/Media/Utils";
import MediaView from "@/components/Media/View";
import Header from "@/components/panels/Media/Header";
import Info from "@/components/panels/Media/Info";
import Nav from "@/components/panels/Media/Nav";
import Results from "@/components/panels/Media/Results";
import Subtitles from "@/components/panels/Media/Subtitles";
import TorrentView from "@/components/panels/Torrent/View";

export default {
  name: "Media",
  mixins: [Utils, MediaUtils],
  components: {Loading, MediaView, Header, Results, Modal, Info, Nav, TorrentView, Subtitles},
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
      awaitingPlayTorrent: null,
      torrentPlugin: null,
      torrentPlugins: [
        'torrent',
        'rtorrent',
      ],
    }
  },

  computed: {
    hasSubtitlesPlugin() {
      return 'media.subtitles' in this.$root.config
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
        await this.download(item)
        return
      }

      if (!this.selectedPlayer.component.supports(item))
        item = await this.startStreaming(item)

      await this.selectedPlayer.component.play(item, this.selectedSubtitles, this.selectedPlayer)
      await this.refresh()
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

    async seek(position) {
      await this.selectedPlayer.component.seek(position, this.selectedPlayer)
      await this.refresh()
    },

    async view(item) {
      const ret = await this.startStreaming(item, true)
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
@import "vars";

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
      height: calc(100% - #{$media-header-height});
      margin-top: .2em;
    }
  }
}

::v-deep(.loading) {
  z-index: 10;
}

::v-deep(.media-info-container) {
  .modal-container {
    .content {
      max-width: 75%;
    }

    .body {
      padding: 1em .5em;
      overflow: auto;
    }
  }
}

::v-deep(.subtitles-container) {
  .body {
    padding: 0 !important;

    .item {
      padding: 1em;
    }
  }
}
</style>

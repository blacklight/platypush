<template>
  <keep-alive>
    <div class="media-plugin fade-in">
      <MediaView :plugin-name="pluginName"
                 :status="selectedPlayer?.status || {}"
                 :track="selectedPlayer?.status || {}"
                 :buttons="mediaButtons"
                 @play="pause"
                 @pause="pause"
                 @stop="stop"
                 @set-volume="setVolume"
                 @seek="seek"
                 @search="search"
                 @mute="toggleMute"
                 @unmute="toggleMute"
      >
        <main>
          <div class="nav-container from tablet" :style="navContainerStyle">
            <Nav :selected-view="selectedView"
                 :torrent-plugin="torrentPlugin"
                 :download-icon-class="downloadIconClass"
                 @input="setView"
                 @toggle="forceShowNav = !forceShowNav"
            />
          </div>

          <div class="view-container">
            <Header :plugin-name="pluginName"
                    :selected-view="selectedView"
                    :has-subtitles-plugin="hasSubtitlesPlugin"
                    :sources="sources"
                    :selected-item="selectedItem"
                    :selected-subtitles="selectedSubtitles"
                    :browser-filter="browserFilter"
                    :downloads-filter="downloadsFilter"
                    :show-nav-button="!forceShowNav"
                    ref="header"
                    @search="search"
                    @select-player="selectedPlayer = $event"
                    @player-status="onStatusUpdate"
                    @torrent-add="downloadTorrent($event)"
                    @show-subtitles="showSubtitlesModal = !showSubtitlesModal"
                    @play-url="showPlayUrlModal"
                    @filter="browserFilter = $event"
                    @filter-downloads="downloadsFilter = $event"
                    @toggle-nav="forceShowNav = !forceShowNav"
                    @source-toggle="sources[$event] = !sources[$event]"
            />

            <div class="body-container" :class="{'expanded-header': $refs.header?.filterVisible}">
              <Results :results="results"
                       :selected-result="selectedResult"
                       :sources="sources"
                       :plugin-name="pluginName"
                       :loading="loading"
                       :filter="browserFilter"
                       @add-to-playlist="addToPlaylistItem = $event"
                       @open-channel="selectChannelFromItem"
                       @select="onResultSelect($event)"
                       @play="play"
                       @view="view"
                       @download="download"
                       @download-audio="downloadAudio"
                       v-if="selectedView === 'search'"
              />

              <TorrentTransfers :plugin-name="torrentPlugin"
                                :is-media="true"
                                @play="play"
                                v-else-if="selectedView === 'torrents'"
              />

              <MediaDownloads :plugin-name="pluginName"
                              :downloads="downloads"
                              :filter="downloadsFilter"
                              @play="play"
                              v-else-if="selectedView === 'downloads'"
              />

              <Browser :filter="browserFilter"
                       :selected-playlist="selectedPlaylist"
                       :selected-channel="selectedChannel"
                       @add-to-playlist="addToPlaylistItem = $event"
                       @back="selectedResult = null"
                       @download="download"
                       @download-audio="downloadAudio"
                       @path-change="browserFilter = ''"
                       @play="play($event)"
                       v-else-if="selectedView === 'browser'"
              />
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

      <div class="add-to-playlist-container" v-if="addToPlaylistItem">
        <Modal title="Add to playlist" :visible="addToPlaylistItem != null" @close="addToPlaylistItem = null">
          <PlaylistAdder
            :item="addToPlaylistItem"
            @done="addToPlaylistItem = null"
            @close="addToPlaylistItem = null"
          />
        </Modal>
      </div>
    </div>
  </keep-alive>
</template>

<script>
import Modal from "@/components/Modal";
import Utils from "@/Utils";

import Browser from "@/components/panels/Media/Browser";
import Header from "@/components/panels/Media/Header";
import MediaDownloads from "@/components/panels/Media/Downloads";
import MediaUtils from "@/components/Media/Utils";
import MediaView from "@/components/Media/View";
import Nav from "@/components/panels/Media/Nav";
import PlaylistAdder from "@/components/panels/Media/PlaylistAdder";
import Results from "@/components/panels/Media/Results";
import Subtitles from "@/components/panels/Media/Subtitles";
import TorrentTransfers from "@/components/panels/Torrent/Transfers";
import UrlPlayer from "@/components/panels/Media/UrlPlayer";

export default {
  name: "Media",
  mixins: [Utils, MediaUtils],
  components: {
    Browser,
    Header,
    MediaDownloads,
    MediaView,
    Modal,
    Nav,
    PlaylistAdder,
    Results,
    Subtitles,
    TorrentTransfers,
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
      prevSelectedView: null,
      showSubtitlesModal: false,
      forceShowNav: false,
      awaitingPlayTorrent: null,
      urlPlay: null,
      browserFilter: null,
      downloadsFilter: null,
      addToPlaylistItem: null,
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

      downloads: {},
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

    selectedPlaylist() {
      if (this.selectedResult == null)
        return null

      const selectedItem = this.results[this.selectedResult]
      if (selectedItem?.item_type !== 'playlist')
        return null

      return this.results[this.selectedResult]
    },

    selectedChannel() {
      if (this.selectedResult == null)
        return null

      const selectedItem = this.results[this.selectedResult]
      if (selectedItem?.item_type !== 'channel')
        return null

      return this.results[this.selectedResult]
    },

    hasPendingDownloads() {
      return Object.values(this.downloads).some((download) => {
        return !['completed', 'cancelled'].includes(download.state.toLowerCase())
      })
    },

    allDownloadsCompleted() {
      return Object.values(this.downloads).length && Object.values(this.downloads).every((download) => {
        return ['completed', 'cancelled'].includes(download.state.toLowerCase())
      })
    },

    downloadIconClass() {
      if (this.hasPendingDownloads)
        return 'glow loop'

      if (this.allDownloadsCompleted)
        return 'completed'

      return ''
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

    async download(item, args) {
      switch (item.type) {
        case 'torrent':
          return await this.downloadTorrent(item, args)
        case 'youtube':
          return await this.downloadYoutube(item, args)
      }
    },

    async downloadAudio(item) {
      await this.download(item, {onlyAudio: true})
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

      if (!item?.url) {
        this.notify({
          text: 'No torrent URL available',
          error: true,
        })

        return
      }

      return await this.request(`${torrentPlugin}.download`, {torrent: item.url || item})
    },

    async downloadYoutube(item, args) {
      if (!item?.url) {
        this.notify({
          text: 'No YouTube URL available',
          error: true,
        })

        return
      }

      const requestArgs = {url: item.url}
      const onlyAudio = !!args?.onlyAudio
      if (onlyAudio) {
        requestArgs.only_audio = true
      }

      await this.request(`${this.pluginName}.download`, requestArgs)
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

      const selectedItem = this.results[this.selectedResult]
      if (this.selectedResult != null && (selectedItem?.item_type === 'playlist' || selectedItem?.item_type === 'channel')) {
        this.onBrowserItemSelect()
      } else {
        this.selectedView = this.prevSelectedView || 'search'
      }
    },

    onBrowserItemSelect() {
      if (this.prevSelectedView != this.selectedView) {
        this.prevSelectedView = this.selectedView
      }

      this.selectedView = 'browser'
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

    async refreshDownloads() {
      this.downloads = (await this.request(`${this.pluginName}.get_downloads`)).reduce((acc, download) => {
        acc[download.path] = download
        return acc
      }, {})
    },

    setView(title) {
      this.selectedView = title
      if (title === 'search') {
        this.selectedResult = null
      }
    },

    updateView() {
      const args = this.getUrlArgs()
      if (args.view) {
        this.selectedView = args.view
      }

      if (args.player && this.players?.length) {
        this.selectedPlayer = this.players.find((player) => player.name === args.player)
      }

      if (args.subtitles) {
        this.selectedSubtitles = args.subtitles
      }
    },

    onDownloadStarted(event) {
      this.downloads[event.path] = event
      this.notify({
        title: 'Media download started',
        html: `Saving <b>${event.resource}</b> to <b>${event.path}</b>`,
        image: {
          iconClass: 'fa fa-download',
        }
      })
    },

    onDownloadCompleted(event) {
      this.downloads[event.path] = event
      this.downloads[event.path].progress = 100

      this.notify({
        title: 'Media download completed',
        html: `Saved <b>${event.resource}</b> to <b>${event.path}</b>`,
        image: {
          iconClass: 'fa fa-check',
        }
      })
    },

    onDownloadError(event) {
      this.downloads[event.path] = event
      this.notify({
        title: 'Media download error',
        html: `Error downloading ${event.resource}: <b>${event.error}</b>`,
        error: true,
        image: {
          iconClass: 'fa fa-exclamation-triangle',
        }
      })
    },

    onDownloadCancelled(event) {
      this.downloads[event.path] = event
      this.notify({
        title: 'Media download cancelled',
        html: `Cancelled download of <b>${event.resource}</b>`,
        image: {
          iconClass: 'fa fa-times',
        }
      })
    },

    onDownloadPaused(event) {
      this.downloads[event.path] = event
      this.notify({
        title: 'Media download paused',
        html: `Paused download of <b>${event.resource}</b>`,
        image: {
          iconClass: 'fa fa-pause',
        }
      })
    },

    onDownloadResumed(event) {
      this.downloads[event.path] = event
      this.notify({
        title: 'Media download resumed',
        html: `Resumed download of <b>${event.resource}</b>`,
        image: {
          iconClass: 'fa fa-play',
        }
      })
    },

    onDownloadProgress(event) {
      this.downloads[event.path] = event
    },

    onDownloadClear(event) {
      if (event.path in this.downloads)
        delete this.downloads[event.path]
    },

    selectChannelFromItem(item) {
      const mediaProvider = item?.type
      const channelId = (
        item?.channel_id ||
        item?.channel?.id ||
        item?.channel_url.split('/').pop()
      )

      if (!mediaProvider && channelId == null)
        return

      this.setUrlArgs({
        provider: mediaProvider,
        section: 'subscriptions',
        channel: channelId,
      })

      this.selectedView = 'browser'
    },
  },

  watch: {
    selectedPlayer(player) {
      this.setUrlArgs({player: player?.name})
      if (player)
        this.refresh()
    },

    selectedSubtitles(subs) {
      this.setUrlArgs({subtitles: this.selectedSubtitles})
      if (new Set(['play', 'pause']).has(this.selectedPlayer?.status?.state)) {
        if (subs)
          this.selectedPlayer.component.addSubtitles(subs)
        else
          this.selectedPlayer.component.removeSubtitles()
      }
    },

    selectedView() {
      this.setUrlArgs({view: this.selectedView})
    },
  },

  async mounted() {
    this.torrentPlugin = this.getTorrentPlugin()
    this.subscribe(this.onTorrentQueued,'on-torrent-queued',
        'platypush.message.event.torrent.TorrentQueuedEvent')
    this.subscribe(this.onTorrentMetadata,'on-torrent-metadata',
        'platypush.message.event.torrent.TorrentDownloadedMetadataEvent')
    this.subscribe(this.onTorrentDownloadStart,'on-torrent-download-start',
        'platypush.message.event.torrent.TorrentDownloadStartEvent')
    this.subscribe(this.onTorrentDownloadCompleted,'on-torrent-download-completed',
        'platypush.message.event.torrent.TorrentDownloadCompletedEvent')

    this.subscribe(this.onDownloadStarted,'on-download-started',
        'platypush.message.event.media.MediaDownloadStartedEvent')
    this.subscribe(this.onDownloadCompleted,'on-download-completed',
        'platypush.message.event.media.MediaDownloadCompletedEvent')
    this.subscribe(this.onDownloadError,'on-download-error',
        'platypush.message.event.media.MediaDownloadErrorEvent')
    this.subscribe(this.onDownloadCancelled,'on-download-cancelled',
        'platypush.message.event.media.MediaDownloadCancelledEvent')
    this.subscribe(this.onDownloadPaused,'on-download-paused',
        'platypush.message.event.media.MediaDownloadPausedEvent')
    this.subscribe(this.onDownloadResumed,'on-download-resumed',
        'platypush.message.event.media.MediaDownloadResumedEvent')
    this.subscribe(this.onDownloadProgress,'on-download-progress',
        'platypush.message.event.media.MediaDownloadProgressEvent')
    this.subscribe(this.onDownloadClear,'on-download-clear',
        'platypush.message.event.media.MediaDownloadClearEvent')

    if ('media.plex' in this.$root.config)
      this.sources.plex = true

    if ('media.jellyfin' in this.$root.config)
      this.sources.jellyfin = true

    await this.refreshDownloads()
    this.updateView()
  },

  destroy() {
    this.unsubscribe('on-torrent-queued')
    this.unsubscribe('on-torrent-metadata')
    this.unsubscribe('on-torrent-download-start')
    this.unsubscribe('on-torrent-download-completed')

    this.unsubscribe('on-download-started')
    this.unsubscribe('on-download-completed')
    this.unsubscribe('on-download-error')
    this.unsubscribe('on-download-cancelled')
    this.unsubscribe('on-download-paused')
    this.unsubscribe('on-download-resumed')
    this.unsubscribe('on-download-progress')
    this.unsubscribe('on-download-clear')
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

:deep(.add-to-playlist-container) {
  .body {
    padding: 0 !important;
  }
}
</style>

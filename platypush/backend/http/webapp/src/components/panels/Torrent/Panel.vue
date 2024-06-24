<template>
  <div class="torrent-container">
    <Modal
      title="Torrent info"
      :visible="infoItem !== null"
      @close="infoIndex = null"
      v-if="infoItem"
    >
      <Info :torrent="infoItem" />
    </Modal>

    <div class="header-container" :class="{'with-nav': !navCollapsed}">
      <Header
        :with-nav="!navCollapsed"
        :selected-view="selectedView"
        :loading="loading"
        @search="search($event)"
        @torrent-add="download($event)"
        @toggle="navCollapsed = !navCollapsed"
      />
    </div>

    <main>
      <div class="view-container" :class="{'with-nav': !navCollapsed}">
        <Transfers
          :transfers="transfers"
          @pause="pause($event)"
          @resume="resume($event)"
          @remove="remove($event)"
          v-if="selectedView === 'transfers'"
        />

        <Results
          :results="results"
          @download="download($event)"
          @info="infoIndex = $event"
          @next-page="search(query, page + 1)"
          v-else-if="selectedView === 'search'"
        />
      </div>

      <div class="nav-container">
        <Nav
          :selected-view="selectedView"
          @toggle="navCollapsed = !navCollapsed"
          @input="selectedView = $event"
          v-if="!navCollapsed"
        />
      </div>
    </main>

  </div>
</template>

<script>
import Info from "./Info";
import Header from "@/components/panels/Torrent/Header";
import Modal from "@/components/Modal";
import Nav from "@/components/panels/Torrent/Nav";
import Results from "@/components/panels/Torrent/Results";
import Transfers from "@/components/panels/Torrent/Transfers";
import Utils from "@/Utils";

export default {
  mixins: [Utils],

  components: {
    Info,
    Header,
    Modal,
    Nav,
    Results,
    Transfers,
  },

  props: {
    pluginName: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      loading: false,
      transfers: {},
      results: [],
      selectedView: "transfers",
      navCollapsed: false,
      query: "",
      page: 1,
      infoIndex: null,
    };
  },

  computed: {
    infoItem() {
      if (this.infoIndex === null) {
        return null
      }

      return this.results[this.infoIndex]
    },
  },

  methods: {
    torrentId(torrent) {
      if (torrent?.hash && torrent.hash.length)
        return torrent.hash

      return torrent.url
    },

    onTorrentUpdate(torrent) {
      this.transfers[this.torrentId(torrent)] = torrent
    },

    onTorrentQueued(torrent) {
      this.onTorrentUpdate(torrent)
      this.notify({
        text: 'Torrent queued for download',
        image: {
          icon: 'hourglass-start',
        }
      })
    },

    onTorrentStart(torrent) {
      this.onTorrentUpdate(torrent)
      this.notify({
        html: `Torrent download started: <b>${torrent.name}</b>`,
        image: {
          icon: 'play',
        }
      })
    },

    onTorrentResume(torrent) {
      this.onTorrentUpdate(torrent)
      this.notify({
        html: `Torrent download resumed: <b>${torrent.name}</b>`,
        image: {
          icon: 'play',
        }
      })
    },

    onTorrentPause(torrent) {
      this.onTorrentUpdate(torrent)
      this.notify({
        html: `Torrent download paused: <b>${torrent.name}</b>`,
        image: {
          icon: 'pause',
        }
      })
    },

    onTorrentCompleted(torrent) {
      this.onTorrentUpdate(torrent)
      this.transfers[this.torrentId(torrent)].finish_date = new Date().toISOString()
      this.transfers[this.torrentId(torrent)].progress = 100
      this.notify({
        html: `Torrent download completed: <b>${torrent.name}</b>`,
        image: {
          icon: 'check',
        }
      })
    },

    onTorrentRemove(torrent) {
      const torrentId = this.torrentId(torrent)
      if (torrentId in this.transfers)
        delete this.transfers[torrentId]
    },

    async search(query, page=1) {
      this.loading = true
      this.query = query
      let results = []

      try {
        results = await this.request(
          `${this.pluginName}.search`,
          {query: query, page: page}
        )
      } finally {
        this.loading = false
      }

      this.results = page === 1 ? results : this.results.concat(results)
      if (results.length > 0) {
        this.page = page
      }
    },

    async download(torrent) {
      await this.request(`${this.pluginName}.download`, {torrent: torrent})
    },

    async pause(torrent) {
      await this.request(`${this.pluginName}.pause`, {torrent: torrent.url})
      await this.refresh()
    },

    async resume(torrent) {
      await this.request(`${this.pluginName}.resume`, {torrent: torrent.url})
      await this.refresh()
    },

    async remove(torrent) {
      await this.request(`${this.pluginName}.remove`, {torrent: torrent.url})
      await this.refresh()
    },

    async refresh() {
      this.loading = true

      try {
        this.transfers = Object.values(await this.request(`${this.pluginName}.status`) || {})
            .reduce((obj, torrent) => {
              obj[this.torrentId(torrent)] = torrent
              return obj
            }, {})
      } finally {
        this.loading = false
      }
    },
  },

  mounted() {
    this.refresh()
    this.selectedView = this.transfers.length ? 'transfers' : 'search'

    this.subscribe(
      this.onTorrentUpdate,
      'on-torrent-update',
      'platypush.message.event.torrent.TorrentDownloadStartEvent',
      'platypush.message.event.torrent.TorrentDownloadProgressEvent',
      'platypush.message.event.torrent.TorrentSeedingStartEvent',
      'platypush.message.event.torrent.TorrentStateChangeEvent',
    )

    this.subscribe(
      this.onTorrentQueued,
      'on-torrent-queued',
      'platypush.message.event.torrent.TorrentQueuedEvent',
    )

    this.subscribe(
      this.onTorrentStart,
      'on-torrent-queued',
      'platypush.message.event.torrent.TorrentDownloadedMetadataEvent',
    )

    this.subscribe(
      this.onTorrentResume,
      'on-torrent-resume',
      'platypush.message.event.torrent.TorrentResumedEvent',
    )

    this.subscribe(
      this.onTorrentPause,
      'on-torrent-pause',
      'platypush.message.event.torrent.TorrentPausedEvent',
    )

    this.subscribe(
      this.onTorrentStop,
      'on-torrent-stop',
      'platypush.message.event.torrent.TorrentDownloadStopEvent',
    )

    this.subscribe(
      this.onTorrentCompleted,
      'on-torrent-completed',
      'platypush.message.event.torrent.TorrentDownloadCompletedEvent'
    )

    this.subscribe(
      this.onTorrentRemove,
      'on-torrent-remove',
      'platypush.message.event.torrent.TorrentRemovedEvent'
    )

    const searchBox = document.querySelector('.search-box input[type="search"]')
    if (searchBox) {
      this.$nextTick(() => searchBox.focus())
    }
  },

  destroy() {
    this.unsubscribe('on-torrent-update')
    this.unsubscribe('on-torrent-remove')
  },
}
</script>

<style lang="scss" scoped>
@import "vars";

.header-container {
  &.with-nav {
    width: calc(100% - #{$torrent-nav-width});
  }
}

.torrent-container {
  width: 100%;
  height: 100%;
  position: relative;

  main {
    width: 100%;
    height: calc(100% - #{$torrent-header-height});
    display: flex;
  }

  .view-container {
    width: 100%;
    height: 100%;
    overflow: auto;
    padding-top: .2em;

    &.with-nav {
      width: calc(100% - #{$torrent-nav-width});
    }
  }
}
</style>

<template>
  <keep-alive>
    <div class="media-plugin fade-in">
      <Loading v-if="loading" />

      <MediaView :plugin-name="pluginName" :status="selectedPlayer?.status || {}" :track="selectedPlayer?.status || {}"
                 :buttons="mediaButtons" @play="pause" @pause="pause" @stop="stop" @set-volume="setVolume"
                 @seek="seek" @search="search">
        <main>
          <Header :plugin-name="pluginName" @search="search" @select-player="selectedPlayer = $event"
                  @player-status="onStatusUpdate" />
          <Results :results="results" :selected-result="selectedResult" @select="selectedResult = $event"
                   @play="play" @info="$refs.mediaInfo.isVisible = true" />
        </main>
      </MediaView>

      <div class="media-info-container">
        <Modal title="Media info" ref="mediaInfo">
          <Info :item="results[selectedResult]" v-if="selectedResult != null" />
        </Modal>
      </div>
    </div>
  </keep-alive>
</template>

<script>
import Loading from "@/components/Loading";
import Modal from "@/components/Modal";
import Utils from "@/Utils";
import MediaView from "@/components/Media/View";
import Header from "@/components/panels/Media/Header";
import Info from "@/components/panels/Media/Info";
import Results from "@/components/panels/Media/Results";

export default {
  name: "Media",
  mixins: [Utils],
  components: {Loading, MediaView, Header, Results, Modal, Info},
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
    }
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
      await this.selectedPlayer.component.play(item, this.selectedPlayer)
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

    async refresh() {
      this.selectedPlayer.status = await this.selectedPlayer.component.status(this.selectedPlayer)
    },

    onStatusUpdate(status) {
      if (!this.selectedPlayer)
        return

      this.selectedPlayer.status = status
    }
  },

  mounted() {
    this.$watch(() => this.selectedPlayer, (player) => {
      if (player)
        this.refresh()
    })
  },
}
</script>

<style lang="scss" scoped>
.media-plugin {
  width: 100%;

  main {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
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
</style>

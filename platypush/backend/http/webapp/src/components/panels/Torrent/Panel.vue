<template>
  <div class="torrent-container">
    <div class="header-container">
      <Header @torrent-add="download($event)" />
    </div>

    <div class="view-container">
      <TorrentView :plugin-name="pluginName" />
    </div>
  </div>
</template>

<script>
import Header from "@/components/panels/Torrent/Header";
import TorrentView from "@/components/panels/Torrent/View";
import Utils from "@/Utils";

export default {
  name: "Panel",
  components: {TorrentView, Header},
  mixins: [Utils],
  props: {
    pluginName: {
      type: String,
      required: true,
    },
  },

  methods: {
    async download(torrent) {
      await this.request(`${this.pluginName}.download`, {torrent: torrent})
    }
  },
}
</script>

<style lang="scss" scoped>
@import "vars";

.torrent-container {
  width: 100%;
  height: calc(100% - #{$torrent-header-height});

  .view-container {
    height: 100%;
    overflow: auto;
    padding-top: .2em;
  }
}
</style>

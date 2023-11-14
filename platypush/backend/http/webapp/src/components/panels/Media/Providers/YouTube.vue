<template>
  <div class="media-youtube-browser">
    <Loading v-if="loading" />

    <div class="browser" v-else>
      <MediaNav :path="computedPath" @back="$emit('back')" />
      <NoToken v-if="!authToken" />

      <div class="body" v-else>
        <Feed @play="$emit('play', $event)" v-if="selectedView === 'feed'" />
        <Playlists :selected-playlist="selectedPlaylist"
                   @play="$emit('play', $event)"
                   @select="onPlaylistSelected"
                   v-else-if="selectedView === 'playlists'" />
        <Index @select="selectView" v-else />
      </div>
    </div>
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import MediaNav from "./Nav";
import MediaProvider from "./Mixin";

import Feed from "./YouTube/Feed";
import Index from "./YouTube/Index";
import NoToken from "./YouTube/NoToken";
import Playlists from "./YouTube/Playlists";

export default {
  mixins: [MediaProvider],
  components: {
    Feed,
    Index,
    Loading,
    MediaNav,
    NoToken,
    Playlists,
  },

  data() {
    return {
      youtubeConfig: null,
      selectedView: null,
      selectedPlaylist: null,
      path: [],
    }
  },

  computed: {
    authToken() {
      return this.youtubeConfig?.auth_token
    },

    computedPath() {
      return [
        {
          title: 'YouTube',
          click: () => this.selectView(null),
          icon: {
            class: 'fab fa-youtube',
          },
        },
        ...this.path,
      ]
    },
  },

  methods: {
    async loadYoutubeConfig() {
      this.loading = true
      try {
        this.youtubeConfig = (await this.request('config.get_plugins')).youtube
      } finally {
        this.loading = false
      }
    },

    selectView(view) {
      this.selectedView = view
      if (view === 'playlists')
        this.selectedPlaylist = null

      if (view?.length) {
        this.path = [
          {
            title: view.slice(0, 1).toUpperCase() + view.slice(1),
            click: () => this.selectView(view),
          },
        ]
      } else {
        this.path = []
      }
    },

    onPlaylistSelected(playlist) {
      this.selectedPlaylist = playlist.id
      this.path.push({
        title: playlist.name,
      })
    },
  },

  mounted() {
    this.loadYoutubeConfig()
  },
}
</script>

<style lang="scss" scoped>
@import "../style.scss";

.media-youtube-browser {
  height: 100%;

  .browser {
    height: 100%;
  }

  .body {
    height: calc(100% - $media-nav-height - 2px);
    margin-top: 2px;
    overflow: auto;
  }
}
</style>

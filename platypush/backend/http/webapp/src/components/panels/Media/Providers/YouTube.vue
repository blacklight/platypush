<template>
  <div class="media-youtube-browser">
    <Loading v-if="loading_" />

    <div class="browser" v-else>
      <MediaNav :path="computedPath" @back="$emit('back')" />
      <NoToken v-if="!authToken" />

      <div class="body" v-else>
        <Feed :filter="filter"
              :loading="isLoading"
              @add-to-playlist="$emit('add-to-playlist', $event)"
              @download="$emit('download', $event)"
              @download-audio="$emit('download-audio', $event)" 
              @open-channel="selectChannelFromItem"
              @play="$emit('play', $event)"
              @play-with-opts="$emit('play-with-opts', $event)"
              @view="$emit('view', $event)"
              v-if="selectedView === 'feed'"
        />

        <Playlists :filter="filter"
                   :loading="isLoading"
                   :selected-playlist="selectedPlaylist_"
                   @add-to-playlist="$emit('add-to-playlist', $event)"
                   @download="$emit('download', $event)"
                   @download-audio="$emit('download-audio', $event)"
                   @open-channel="selectChannelFromItem"
                   @play="$emit('play', $event)"
                   @play-with-opts="$emit('play-with-opts', $event)"
                   @remove-from-playlist="removeFromPlaylist"
                   @select="onPlaylistSelected"
                   @view="$emit('view', $event)"
                   v-else-if="selectedView === 'playlists'"
        />

        <Subscriptions :filter="filter"
                       :loading="isLoading"
                       :selected-channel="selectedChannel_"
                       @add-to-playlist="$emit('add-to-playlist', $event)"
                       @download="$emit('download', $event)"
                       @download-audio="$emit('download-audio', $event)"
                       @play="$emit('play', $event)"
                       @play-with-opts="$emit('play-with-opts', $event)"
                       @select="onChannelSelected"
                       @view="$emit('view', $event)"
                       v-else-if="selectedView === 'subscriptions'"
        />

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
import Subscriptions from "./YouTube/Subscriptions";

export default {
  mixins: [MediaProvider],
  components: {
    Feed,
    Index,
    Loading,
    MediaNav,
    NoToken,
    Playlists,
    Subscriptions,
  },

  emits: [
    'add-to-playlist',
    'back',
    'download',
    'download-audio',
    'play',
    'play-with-opts',
    'view',
  ],

  data() {
    return {
      youtubeConfig: null,
      selectedView: null,
      selectedPlaylist_: null,
      selectedChannel_: null,
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
      this.loading_ = true
      try {
        this.youtubeConfig = (await this.request('config.get_plugins')).youtube
      } finally {
        this.loading_ = false
      }
    },

    async removeFromPlaylist(event) {
      const playlistId = event.playlist_id
      const videoId = event.item.url
      this.loading_ = true

      try {
        await this.request('youtube.remove_from_playlist', {
          playlist_id: playlistId,
          video_id: videoId,
        })
      } finally {
        this.loading_ = false
      }
    },

    async createPlaylist(name) {
      this.loading_ = true
      try {
        await this.request('youtube.create_playlist', {name: name})
      } finally {
        this.loading_ = false
      }
    },

    selectView(view) {
      this.selectedView = view
      if (view === 'playlists')
        this.selectedPlaylist_ = null
      else if (view === 'subscriptions')
        this.selectedChannel_ = null

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
      this.selectedPlaylist_ = playlist
      if (!playlist)
        return

      this.selectedView = 'playlists'
      this.path.push({
        title: playlist.name,
      })
    },

    onChannelSelected(channel) {
      this.selectedChannel_ = channel
      if (!channel)
        return

      this.selectedView = 'subscriptions'
      this.path.push({
        title: channel.name,
      })
    },

    initView() {
      const args = this.getUrlArgs()

      if (args.section)
        this.selectedView = args.section

      if (this.selectedView)
        this.selectView(this.selectedView)
    },

    async selectChannelFromItem(item) {
      if (!item.channel_url)
        return

      const channel = await this.request(
        'youtube.get_channel',
        {id: item.channel_url.split('/').pop()}
      )

      if (!channel)
        return

      this.onChannelSelected(channel)
    },
  },

  watch: {
    selectedPlaylist() {
      this.onPlaylistSelected(this.selectedPlaylist)
    },

    selectedPlaylist_(value) {
      if (value == null)
        this.setUrlArgs({playlist: null})
    },

    selectedChannel() {
      this.onChannelSelected(this.selectedChannel)
    },

    selectedChannel_(value) {
      if (value == null)
        this.setUrlArgs({channel: null})
    },

    selectedView() {
      this.setUrlArgs({section: this.selectedView})
    },
  },

  mounted() {
    this.loadYoutubeConfig()
    this.initView()
    this.onPlaylistSelected(this.selectedPlaylist)
    this.onChannelSelected(this.selectedChannel)
  },

  unmounted() {
    this.setUrlArgs({section: null})
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
    overflow-y: auto;
  }
}
</style>

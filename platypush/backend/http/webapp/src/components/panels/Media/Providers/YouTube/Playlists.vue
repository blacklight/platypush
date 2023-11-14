<template>
  <div class="media-youtube-playlists">
    <div class="playlists-index" v-if="!selectedPlaylist">
      <Loading v-if="loading" />
      <NoItems :with-shadow="false" v-else-if="!playlists?.length">
        No playlists found.
      </NoItems>

      <div class="body grid" v-else>
        <div class="playlist item"
             v-for="(playlist, id) in playlistsById"
             :key="id"
             @click="selectedPlaylist = id">
          <MediaImage :item="playlist" :has-play="false" />
          <div class="title">{{ playlist.name }}</div>
        </div>
      </div>
    </div>

    <div class="playlist-body" v-else>
      <Playlist :id="selectedPlaylist" @play="$emit('play', $event)" />
    </div>
  </div>
</template>

<script>
import MediaImage from "@/components/panels/Media/MediaImage";
import NoItems from "@/components/elements/NoItems";
import Loading from "@/components/Loading";
import Playlist from "./Playlist";
import Utils from "@/Utils";

export default {
  emits: ['play'],
  mixins: [Utils],
  components: {
    Loading,
    MediaImage,
    NoItems,
    Playlist,
  },

  data() {
    return {
      playlists: [],
      loading: false,
      selectedPlaylist: null,
    }
  },

  computed: {
    playlistsById() {
      return this.playlists.reduce((acc, playlist) => {
        acc[playlist.id] = playlist
        return acc
      }, {})
    },
  },

  methods: {
    async loadPlaylists() {
      this.loading = true
      try {
        this.playlists = (await this.request('youtube.get_playlists'))
      } finally {
        this.loading = false
      }
    },
  },

  mounted() {
    this.loadPlaylists()
  },
}
</script>

<style lang="scss" scoped>
.media-youtube-playlists {
  height: 100%;
  overflow: auto;

  .item {
    cursor: pointer;

    &:hover {
      text-decoration: underline;
    }
  }
}
</style>

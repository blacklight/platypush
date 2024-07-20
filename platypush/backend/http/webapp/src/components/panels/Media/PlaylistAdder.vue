<template>
  <div class="playlist-adder-container">
    <Loading v-if="loading" />
    <TextPrompt ref="newPlaylistName" :visible="showNewPlaylist" @input="createPlaylist($event)">
      Playlist name
    </TextPrompt>

    <div class="playlists">
      <div class="playlist new-playlist">
        <button @click="showNewPlaylist = true">
          <i class="fa fa-plus" />
          Create new playlist
        </button>
      </div>

      <div class="playlist" v-for="playlist in playlists" :key="playlist.id">
        <button @click="addToPlaylist(playlist.id)">
          <i class="fa fa-list" />
          {{ playlist.name }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import Utils from "@/Utils";
import TextPrompt from "@/components/elements/TextPrompt"

export default {
  emits: ['done'],
  mixins: [Utils],
  components: {Loading, TextPrompt},
  props: {
    item: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      loading: false,
      playlists: [],
      showNewPlaylist: false,
    }
  },

  methods: {
    async createPlaylist(name) {
      name = name?.trim()
      if (!name?.length)
        return

      this.loading = true

      try {
        const playlist = await this.request('youtube.create_playlist', {
          name: name,
        })

        await this.request('youtube.add_to_playlist', {
          playlist_id: playlist.id,
          video_id: this.item.id || this.item.url,
        })

        this.$emit('done')
        this.notify({
          text: 'Playlist created and video added',
          image: {
            icon: 'check',
          }
        })

      } finally {
        this.loading = false
        this.showNewPlaylist = false
      }
    },

    async refreshPlaylists() {
      this.loading = true

      try {
        this.playlists = await this.request('youtube.get_playlists')
      } finally {
        this.loading = false
      }
    },

    async addToPlaylist(playlistId) {
      this.loading = true

      try {
        await this.request('youtube.add_to_playlist', {
          playlist_id: playlistId,
          video_id: this.item.id || this.item.url,
        })

        this.notify({
          text: 'Video added to playlist',
          image: {
            icon: 'check',
          }
        })

        this.$emit('done')
      } finally {
        this.loading = false
      }
    },
  },

  mounted() {
    this.refreshPlaylists()
  },
}
</script>

<style lang="scss" scoped>
.playlist-adder-container {
  min-width: 300px;
  height: 100%;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;

  .playlists {
    width: 100%;
    overflow-y: auto;
  }

  .playlist {
    button {
      width: 100%;
      text-align: left;
      padding: 0.5em 1em;
      border: none;
      background: none;
      cursor: pointer;
      transition: background 0.2s, color 0.2s;

      &:hover {
        background: $hover-bg;
      }

      i {
        margin-right: 0.5em;
      }
    }
  }

  .new-playlist {
    button {
      font-weight: bold;
      border-bottom: $default-border;
    }
  }
}
</style>

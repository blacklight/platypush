<template>
  <div class="playlist-adder-container">
    <Loading v-if="loading" />
    <TextPrompt ref="newPlaylistName" :visible="showNewPlaylist" @input="createPlaylist($event)">
      Playlist name
    </TextPrompt>

    <div class="playlists-container">
      <div class="header">
        <div class="filter">
          <input type="text"
                 placeholder="Filter playlists"
                 ref="playlistFilter"
                 @input="filter = $event.target.value">
        </div>

        <div class="playlist new-playlist">
          <button @click="showNewPlaylist = true">
            <i class="fa fa-plus" />
            Create new playlist
          </button>
        </div>
      </div>

      <div class="playlists">
        <div class="playlist" v-for="playlist in sortedPlaylists" :key="playlist.id">
          <button @click="addToPlaylist(playlist.id)">
            <i class="fa fa-list" />
            {{ playlist.name }}
          </button>
        </div>
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
      filter: '',
      loading: false,
      playlists: [],
      showNewPlaylist: false,
    }
  },

  computed: {
    pluginName() {
      switch (this.item.type) {
        case 'youtube':
          return 'youtube'

        case 'jellyfin':
          return 'media.jellyfin'

        default:
          return null
      }
    },

    sortedPlaylists() {
      return this.playlists
        .filter((playlist) => playlist.name.toLowerCase().includes(this.filter.toLowerCase()))
        .sort((a, b) => a.name.localeCompare(b.name))
    },
  },

  methods: {
    checkPlugin() {
      if (!this.pluginName) {
        this.notify({
          title: 'Unsupported item type',
          text: `Item type ${this.item.type} does not support playlists`,
          warning: true,
          image: {
            icon: 'exclamation-triangle',
          }
        })

        console.warn(`Unsupported item type: ${this.item.type}`)
        return false
      }

      return true
    },

    async createPlaylist(name) {
      name = name?.trim()
      if (!name?.length)
        return

      this.loading = true

      try {
        const playlist = await this.request(`${this.pluginName}.create_playlist`, {
          name: name,
        })

        await this.addToPlaylist(playlist.id)
      } finally {
        this.loading = false
        this.showNewPlaylist = false
      }
    },

    async refreshPlaylists() {
      if (!this.checkPlugin())
        return

      this.loading = true
      try {
        this.playlists = await this.request(`${this.pluginName}.get_playlists`)
      } finally {
        this.loading = false
      }
    },

    async addToPlaylist(playlistId) {
      if (!this.checkPlugin())
        return

      this.loading = true
      try {
        await this.request(`${this.pluginName}.add_to_playlist`, {
          playlist_id: playlistId,
          item_ids: [this.item.id || this.item.url],
        })

        this.notify({
          text: 'Item added to playlist',
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

  watch: {
    loading() {
      if (this.loading)
        return

      this.$nextTick(() => this.$refs.playlistFilter.focus())
    },
  },

  mounted() {
    this.refreshPlaylists()
  },
}
</script>

<style lang="scss" scoped>
$header-height: 6.5em;

.playlist-adder-container {
  width: 30em;
  height: fit-content;
  max-width: 90vw;
  max-height: 70vh;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;

  .playlists-container {
    width: 100%;
    height: 100%;

    .header {
      width: 100%;
      height: $header-height;
      display: flex;
      flex-direction: column;
    }
  }

  .playlists {
    width: 100%;
    height: calc(100% - #{$header-height});
    overflow-y: auto;
  }

  .filter {
    width: 100%;
    display: flex;

    input[type="text"] {
      width: 100%;
      margin: 0.5em 0.5em 0.25em 0.5em;
      padding: 0.5em;
    }
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

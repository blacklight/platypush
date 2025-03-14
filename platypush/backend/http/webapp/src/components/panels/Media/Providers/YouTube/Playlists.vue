<template>
  <div class="media-youtube-playlists">
    <div class="playlists-index" v-if="!selectedPlaylist?.id">
      <Loading v-if="showLoading" />
      <NoItems :with-shadow="false" v-else-if="!playlists?.length">
        No playlists found.
      </NoItems>

      <div class="body grid" ref="body" @scroll="onScroll" v-else>
        <div class="playlist item"
             v-for="(playlist, id) in playlistsById"
             :key="id"
             @click="$emit('select', playlist)">
          <MediaImage :item="playlist" :has-play="false" />
          <div class="title">{{ playlist.name }}</div>
          <div class="actions">
            <button title="Remove" @click.stop="deletedPlaylist = playlist.id">
              <i class="fa fa-trash" />
            </button>
            <button title="Edit" @click.stop="editedPlaylist = playlist.id">
              <i class="fa fa-pencil" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="playlist-body" v-else>
      <Playlist
        :id="selectedPlaylist.id"
        :filter="filter"
        :metadata="playlistsById[selectedPlaylist.id] || selectedPlaylist"
        @add-to-playlist="$emit('add-to-playlist', $event)"
        @download="$emit('download', $event)"
        @download-audio="$emit('download-audio', $event)"
        @open-channel="$emit('open-channel', $event)"
        @remove-from-playlist="$emit('remove-from-playlist', {item: $event, playlist_id: selectedPlaylist.id})"
        @play="$emit('play', $event)"
        @play-with-opts="$emit('play-with-opts', $event)"
        @view="$emit('view', $event)"
      />
    </div>

    <TextPrompt
      :visible="showCreatePlaylist"
      @input="createPlaylist($event)"
      @close="showCreatePlaylist = false"
    >
      Playlist name
    </TextPrompt>

    <ConfirmDialog
      ref="removePlaylist"
      title="Remove Playlist"
      :visible="deletedPlaylist != null"
      @input="removePlaylist"
    >
      Are you sure you want to remove this playlist?
    </ConfirmDialog>

    <Modal
      ref="editPlaylist"
      title="Edit Playlist"
      :visible="editedPlaylist != null"
      @close="clearEditPlaylist"
      @open="onEditPlaylistOpen"
    >
      <form class="edit-playlist-form" @submit.prevent="editPlaylist">
        <div class="row">
          <input ref="editPlaylistName" placeholder="Playlist name" v-model="editedPlaylistName" />
        </div>

        <div class="row">
          <input placeholder="Playlist description" v-model="editedPlaylistDescription" />
        </div>

        <div class="row buttons">
          <div class="btn-container col-6">
            <button type="submit">
              <i class="fa fa-check" />&nbsp;Save
            </button>
          </div>

          <div class="btn-container col-6">
            <button @click="clearEditPlaylist">
              <i class="fa fa-times" />&nbsp;Cancel
            </button>
          </div>
        </div>
      </form>
    </Modal>

    <FloatingButton
      icon-class="fa fa-plus"
      title="Create Playlist"
      @click="showCreatePlaylist = true"
    />
  </div>
</template>

<script>
import ConfirmDialog from "@/components/elements/ConfirmDialog";
import FloatingButton from "@/components/elements/FloatingButton";
import MediaImage from "@/components/panels/Media/MediaImage";
import Modal from "@/components/Modal";
import NoItems from "@/components/elements/NoItems";
import Loading from "@/components/Loading";
import Playlist from "./Playlist";
import TextPrompt from "@/components/elements/TextPrompt"
import Utils from "@/Utils";

export default {
  mixins: [Utils],
  emits: [
    'add-to-playlist',
    'create-playlist',
    'download',
    'download-audio',
    'open-channel',
    'play',
    'play-with-opts',
    'remove-from-playlist',
    'remove-playlist',
    'rename-playlist',
    'select',
  ],

  components: {
    ConfirmDialog,
    FloatingButton,
    Loading,
    MediaImage,
    Modal,
    NoItems,
    Playlist,
    TextPrompt,
  },

  props: {
    selectedPlaylist: {
      type: Object,
      default: null,
    },

    filter: {
      type: String,
      default: null,
    },

    loading: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      deletedPlaylist: null,
      editedPlaylist: null,
      editedPlaylistName: '',
      editedPlaylistDescription: '',
      nextPageToken: null,
      playlists: [],
      initialLoading: true,
      loading_: false,
      renderedPageTokens: {},
      showCreatePlaylist: false,
    }
  },

  computed: {
    playlistsById() {
      return this.playlists
        .filter(playlist => !this.filter || playlist.name.toLowerCase().includes(this.filter.toLowerCase()))
        .reduce((acc, playlist) => {
          acc[playlist.id] = playlist
          return acc
        }, {})
    },

    showLoading() {
      return this.initialLoading && (this.loading_ || this.loading)
    },
  },

  methods: {
    async onScroll() {
      const offset = this.$refs.body.scrollTop
      const bodyHeight = parseFloat(getComputedStyle(this.$refs.body).height)
      const scrollHeight = this.$refs.body.scrollHeight

      if (offset >= (scrollHeight - bodyHeight - 5)) {
        if (
          this.scrollTimeout ||
          !this.playlists.length ||
          this.renderedPageTokens[this.nextPageToken]
        )
          return

        this.scrollTimeout = setTimeout(() => {
          this.scrollTimeout = null
        }, 1000)

        await this.loadPlaylists()
      }
    },

    async loadPlaylists() {
      this.loading_ = true
      try {
        this.playlists = [
          ...this.playlists,
          ...(await this.request('youtube.get_playlists', {page: this.nextPageToken})),
        ]

        this.initialLoading = false
        if (this.nextPageToken) {
          this.renderedPageTokens[this.nextPageToken] = true
        }

        if (this.playlists.length) {
          this.nextPageToken = this.playlists[this.playlists.length - 1].next_page_token
        }
      } finally {
        this.loading_ = false
      }
    },

    async createPlaylist(name) {
      this.loading_ = true

      try {
        const playlist = await this.request('youtube.create_playlist', {name: name})
        this.showCreatePlaylist = false
        this.playlists = [playlist, ...this.playlists]
      } finally {
        this.loading_ = false
      }
    },

    async removePlaylist() {
      if (!this.deletedPlaylist)
        return

      this.loading_ = true

      try {
        await this.request('youtube.delete_playlist', {id: this.deletedPlaylist})
        this.playlists = this.playlists.filter(playlist => playlist.id !== this.deletedPlaylist)
        this.deletedPlaylist = null
      } finally {
        this.loading_ = false
      }
    },

    async editPlaylist() {
      if (!this.editedPlaylist)
        return

      this.loading_ = true
      try {
        await this.request('youtube.edit_playlist', {
          id: this.editedPlaylist,
          name: this.editedPlaylistName,
          description: this.editedPlaylistDescription,
        })

        this.clearEditPlaylist()
        this.loadPlaylists()
      } finally {
        this.loading_ = false
      }
    },

    clearEditPlaylist() {
      this.editedPlaylist = null
      this.editedPlaylistName = ''
      this.editedPlaylistDescription = ''
      this.$refs.editPlaylist.hide()
    },

    onEditPlaylistOpen() {
      const playlist = this.playlistsById[this.editedPlaylist]
      this.editedPlaylistName = playlist.name
      this.editedPlaylistDescription = playlist.description
      this.$nextTick(() => this.$refs.editPlaylistName.focus())
    },
  },

  async mounted() {
    await this.loadPlaylists()

    const args = this.getUrlArgs()
    if (args.playlist) {
      const playlist = this.playlistsById[args.playlist]
      if (playlist) {
        this.$emit('select', playlist)
      } else {
        this.$emit('select', {id: args.playlist})
      }
    }
  },

  unmouted() {
    this.setUrlArgs({section: null})
  },
}
</script>

<style lang="scss" scoped>
.media-youtube-playlists {
  height: 100%;
  position: relative;

  .playlists-index {
    height: 100%;
  }

  .body, .playlist-body {
    height: 100%;
  }

  .body {
    overflow-y: auto;
  }

  :deep(.playlist.item) {
    position: relative;
    cursor: pointer;

    .title {
      font-size: 1.1em;
      margin-top: 0.5em;
    }

    .actions {
      position: absolute;
      top: 0;
      right: 0;
      display: flex;
      padding: 0.5em;
      background: rgba(0, 0, 0, 0.25);
      opacity: 0.9;
      border-radius: 0 0 0.5em 0.5em;
      transition: opacity 0.2s;
      z-index: 1;

      button {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        transition: transform 0.2s;
        flex: 1;

        &:hover {
          color: $default-hover-fg;
          transform: scale(1.2);
        }
      }
    }

    &:hover {
      text-decoration: underline;

      img {
        filter: contrast(70%);
      }
    }
  }

  :deep(.modal) {
    .edit-playlist-form {
      min-width: 300px;
      display: flex;
      flex-direction: column;

      .row {
        margin: 0.5em 0;

        input {
          border: $default-border;
          border-radius: 1em;
          padding: 0.5em;
          width: 100%;

          &:focus {
            border: 1px solid $selected-fg;
          }
        }

        &.buttons {
          display: flex;
          justify-content: flex-end;
          margin-top: 0.5em;

          .btn-container {
            display: flex;
            justify-content: center;
          }
        }

        button {
          margin: 0 0.5em;
          padding: 0.5em;
          border-radius: 1em;
          cursor: pointer;
          transition: background 0.2s;

          &:hover {
            background: $hover-bg;
          }
        }
      }
    }
  }
}
</style>

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
        :id="selectedPlaylist"
        :filter="filter"
        :playlist="playlist"
        @add-to-playlist="$emit('add-to-playlist', $event)"
        @remove-from-playlist="$emit('remove-from-playlist', {item: $event, playlist_id: selectedPlaylist})"
        @play="$emit('play', $event)"
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
      @close="deletedPlaylist = null"
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
    'play',
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
      type: String,
      default: null,
    },

    filter: {
      type: String,
      default: null,
    },
  },

  data() {
    return {
      deletedPlaylist: null,
      editedPlaylist: null,
      editedPlaylistName: '',
      editedPlaylistDescription: '',
      playlists: [],
      loading: false,
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

    async createPlaylist(name) {
      this.loading = true
      try {
        await this.request('youtube.create_playlist', {name: name})
        this.showCreatePlaylist = false
        this.loadPlaylists()
      } finally {
        this.loading = false
      }
    },

    async removePlaylist() {
      if (!this.deletedPlaylist)
        return

      this.loading = true
      try {
        await this.request('youtube.delete_playlist', {id: this.deletedPlaylist})
        this.deletedPlaylist = null
        this.loadPlaylists()
      } finally {
        this.loading = false
      }
    },

    async editPlaylist() {
      if (!this.editedPlaylist)
        return

      this.loading = true
      try {
        await this.request('youtube.rename_playlist', {
          id: this.editedPlaylist,
          name: this.editedPlaylistName,
          description: this.editedPlaylistDescription,
        })

        this.clearEditPlaylist()
        this.loadPlaylists()
      } finally {
        this.loading = false
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

  mounted() {
    this.loadPlaylists()
  },
}
</script>

<style lang="scss" scoped>
.media-youtube-playlists {
  height: 100%;
  position: relative;

  .playlist-body {
    height: 100%;
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

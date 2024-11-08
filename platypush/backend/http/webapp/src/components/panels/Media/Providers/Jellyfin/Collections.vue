<template>
  <div class="collections index" :class="{ 'is-root': !parentId }">
    <div class="collections items">
      <div class="collection item"
           v-for="collection in filteredItems"
           :key="collection.id"
           @click="$emit('select', collection)">
        <div class="image">
          <img :src="collection.image"
               :alt="collection.name"
               @error="onImageError(collection)"
               v-if="!fallbackImageCollections[collection.id]">
          <i :class="collectionsIcons[collection.type] ?? 'fas fa-folder'" v-else />
        </div>

        <div class="name" v-if="fallbackImageCollections[collection.id] || parentId">
          <h2>{{ collection.name }}</h2>
        </div>

        <div class="float bottom-right" v-if="collection.year">
          <span>{{ collection.year }}</span>
        </div>
      </div>
    </div>

    <div class="add-playlist floating-btn-container" v-if="isPlaylistsCollection">
      <FloatingButton icon-class="fa fa-plus"
                      title="Create Playlist"
                      :disabled="loading"
                      @click="showNewPlaylist = true" />
    </div>

    <div class="add-playlist-modal" v-if="showNewPlaylist">
      <Modal title="Create Playlist"
             :visible="true"
             @close="showNewPlaylist = false">
        <form class="modal-body" @submit.prevent="createPlaylist">
          <div class="row">
            <label for="newPlaylistName">Playlist Name</label>
            <input name="name"
                   type="text"
                   id="newPlaylistName"
                   placeholder="Playlist Name"
                   required>
          </div>

          <div class="row">
            <label for="newPlaylistPublic">Public</label>
            <input name="public" type="checkbox" checked id="newPlaylistPublic">
          </div>

          <div class="row buttons">
            <button type="button" @click="showNewPlaylist = false">Cancel</button>
            <button type="submit">Create</button>
          </div>
        </form>
      </Modal>
    </div>
  </div>
</template>

<script>
import FloatingButton from "@/components/elements/FloatingButton";
import Modal from "@/components/Modal";
import Utils from '@/Utils'

export default {
  mixins: [Utils],
  emits: ['refresh', 'select'],
  components: {
    FloatingButton,
    Modal,
  },

  props: {
    collection: {
      type: Object,
    },

    filter: {
      type: String,
    },

    items: {
      type: Array,
      default: () => [],
    },

    batchItems: {
      type: Number,
      default: 100,
    },

    parentId: {
      type: String,
    },
  },

  data() {
    return {
      fallbackImageCollections: {},
      loading: false,
      maxResultIndex: this.batchItems,
      showNewPlaylist: false,
    };
  },

  computed: {
    collectionsIcons() {
      return {
        books: "fas fa-book",
        homevideos: "fas fa-video",
        movies: "fas fa-film",
        music: "fas fa-music",
        playlists: "fas fa-list",
        photos: "fas fa-image",
        series: "fas fa-tv",
      };
    },

    filteredItems() {
      return Object.values(this.items).filter(
        (item) => !this.filter || item.name.toLowerCase().includes(this.filter.toLowerCase())
      ).sort((a, b) => {
        if (a.item_type === 'album' && b.item_type === 'album') {
          if (a.year && b.year) {
            if (a.year !== b.year) {
              return b.year - a.year
            }
          }
        }

        return a.name.localeCompare(b.name)
      }).slice(0, this.maxResultIndex)
    },

    isPlaylistsCollection() {
      return this.collection?.collection_type === 'playlists'
    },
  },

  methods: {
    async createPlaylist(event) {
      const form = new FormData(event.target)
      await this.request('media.jellyfin.create_playlist', {
        name: form.get('name'),
        public: form.get('public') === 'on',
      })

      this.$emit('refresh')
    },

    onImageError(collection) {
      this.fallbackImageCollections[collection.id] = true
    },

    onScroll(e) {
      const el = e.target
      if (!el)
        return

      const bottom = (el.scrollHeight - el.scrollTop) <= el.clientHeight + 150
      if (!bottom)
        return

      this.maxResultIndex += this.batchItems
    },
  },

  watch: {
    showNewPlaylist(value) {
      if (value)
        this.$nextTick(() => this.$el.querySelector('input[name="name"]').focus())
    },
  },

  mounted() {
    this.$el.parentElement?.addEventListener('scroll', this.onScroll)
  },

  unmounted() {
    this.$el.parentElement?.removeEventListener('scroll', this.onScroll)
  },
}
</script>

<style lang="scss" scoped>
@import "./common.scss";

.index {
  .item {
    position: relative;

    h2 {
      font-size: 1.25em;
      font-weight: bold;
      overflow: auto;
      text-overflow: ellipsis;
    }

    .float {
      position: absolute;
      background: rgba(0, 0, 0, 0.5);
      color: white;
      z-index: 1;
      padding: 0.25em;
      font-size: 0.9em;
      border-radius: 0.5em;

      &.bottom-right {
        right: 0;
        bottom: 0;
      }
    }
  }

  &.is-root {
    .item {
      h2 {
        font-size: 2em;
      }
    }
  }

  :deep(.add-playlist-modal) {
    .modal-body {
      min-width: 30em;
      max-width: calc(100% - 2em);
    }

    form {
      display: flex;
      flex-direction: column;

      .row {
        margin-bottom: 1em;

        label {
          @extend .col-m-4;
          @extend .col-s-12;
        }

        input {
          @extend .col-m-8;
          @extend .col-s-12;
        }

        &.buttons {
          display: flex;
          justify-content: flex-end;

          button {
            margin-left: 1em;

            &[type="submit"] {
              width: 10em;
              cursor: pointer;
            }
          }
        }
      }
    }
  }
}
</style>

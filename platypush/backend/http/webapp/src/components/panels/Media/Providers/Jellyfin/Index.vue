<template>
  <div class="collections index">
    <Loading v-if="isLoading" />

    <div class="collections items" v-else>
      <div class="collection item"
           v-for="collection in filteredCollections"
           :key="collection.id"
           @click="$emit('select', collection)">
        <div class="image">
          <img :src="collection.image"
               :alt="collection.name"
               @error="onImageError(collection)"
               v-if="!fallbackImageCollections[collection.id]">
          <i :class="collectionsIcons[collection.type] ?? 'fas fa-folder'" v-else />
        </div>

        <div class="name" v-if="fallbackImageCollections[collection.id]">
          <h2>{{ collection.name }}</h2>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import MediaProvider from "../Mixin";

export default {
  mixins: [MediaProvider],
  components: {
    Loading,
  },

  emits: [
    'add-to-playlist',
    'back',
    'download',
    'download-audio',
    'play',
    'play-with-opts',
    'select',
  ],

  data() {
    return {
      collections: {},
      fallbackImageCollections: {},
      loading_: false,
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

    filteredCollections() {
      return Object.values(this.collections).filter(
        (collection) => !this.filter || collection.name.toLowerCase().includes(this.filter.toLowerCase())
      );
    },

    isLoading() {
      return this.loading_ || this.loading
    },
  },

  methods: {
    onImageError(collection) {
        this.fallbackImageCollections[collection.id] = true
    },

    async refresh() {
      this.loading_ = true

      try {
        this.collections = (
          await this.request('media.jellyfin.get_collections')
        ).reduce((acc, collection) => {
          acc[collection.id] = collection
          return acc
        }, {})
      } finally {
        this.loading_ = false
      }
    },

    initCollection() {
      const collectionId = this.getUrlArgs().collection
      if (collectionId == null) {
        return
      }

      const collection = this.collections[collectionId]
      if (!collection) {
        return
      }

      this.$emit('select', collection)
    },
  },

  async mounted() {
    await this.refresh()
    this.initCollection()
  },
}
</script>

<style lang="scss" scoped>
@import "./common.scss";

.index {
  .item {
    h2 {
      font-size: 2em;
      font-weight: bold;
    }
  }
}
</style>

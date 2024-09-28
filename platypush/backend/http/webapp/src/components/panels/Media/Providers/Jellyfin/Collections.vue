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
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    filter: {
      type: String,
    },

    items: {
      type: Array,
      default: () => [],
    },

    parentId: {
      type: String,
    },
  },

  data() {
    return {
      fallbackImageCollections: {},
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
      ).sort((a, b) => a.name.localeCompare(b.name))
    },
  },

  methods: {
    onImageError(collection) {
      this.fallbackImageCollections[collection.id] = true
    },
  },
}
</script>

<style lang="scss" scoped>
@import "./common.scss";

.index {
  .item {
    h2 {
      font-size: 1.25em;
      font-weight: bold;
      overflow: auto;
      text-overflow: ellipsis;
    }
  }

  &.is-root {
    .item {
      h2 {
        font-size: 2em;
      }
    }
  }
}
</style>

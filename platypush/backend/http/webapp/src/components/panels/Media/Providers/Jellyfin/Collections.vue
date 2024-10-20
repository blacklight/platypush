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
      maxResultIndex: this.batchItems,
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
  },

  methods: {
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
}
</style>

<template>
  <div class="media-jellyfin-container browser">
    <MediaNav :path="path" @back="$emit('back')" @select="select" />

    <div class="media-jellyfin-browser">
      <Loading v-if="isLoading" />

      <Movies v-bind="componentData.props"
              v-on="componentData.on"
              :collection="collection"
              @select="select"
              @view="$emit('view', $event)"
              v-else-if="currentView === 'movies'" />

      <Media v-bind="componentData.props"
             v-on="componentData.on"
             :collection="collection"
             @delete="deleteItem"
             @select="select"
             @select-collection="selectCollection"
             @view="$emit('view', $event)"
             v-else />
    </div>
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import MediaNav from "./Nav";
import MediaProvider from "./Mixin";
import Media from "./Jellyfin/views/Media/Index";
import Movies from "./Jellyfin/views/Movies/Index";

export default {
  mixins: [MediaProvider],
  components: {
    Loading,
    MediaNav,
    Media,
    Movies,
  },

  emits: [
    'add-to-playlist',
    'back',
    'download',
    'path-change',
    'play',
    'play-with-opts',
    'view',
  ],

  data() {
    return {
      collection: null,
      loading_: false,
      path: [],
    };
  },

  computed: {
    componentData() {
      return {
        props: {
          collection: this.collection,
          filter: this.filter,
          loading: this.isLoading,
          path: this.path,
        },

        on: {
          'add-to-playlist': (item) => this.$emit('add-to-playlist', item),
          'download': (item) => this.$emit('download', item),
          'play': (item) => this.$emit('play', item),
          'play-with-opts': (item) => this.$emit('play-with-opts', item),
        },
      }
    },

    currentView() {
      if (!this.collection) {
        return 'index'
      }

      switch (this.collection.collection_type) {
        case 'movies':
          return 'movies'
        case 'homevideos':
          return 'videos'
        case 'music':
          return 'music'
        default:
          return 'index'
      }
    },

    isLoading() {
      return this.loading_ || this.loading
    },

    rootItem() {
      const item = {
        id: '',
        title: 'Jellyfin',
        type: 'index',
        icon: {
          class: 'fas fa-server',
        },
      }

      item.click = () => {
        this.collection = null
        this.select(item)
      }

      return item
    },
  },

  methods: {
    select(item) {
      if (item) {
        if (this.path.length > 0 && this.path[this.path.length - 1].id === item.id) {
          return
        }

        if (item.type === 'index') {
          this.path = [this.rootItem]
        } else {
          const itemIndex = this.path.findIndex((i) => i.id === item.id)
          if (itemIndex >= 0) {
            this.path = this.path.slice(0, itemIndex + 1)
          } else {
            this.path.push({
              title: item.name,
              click: () => this.selectCollection(item),
              ...item,
            })
          }
        }
      } else {
        this.path = []
      }

      this.$emit('path-change', this.path)
    },

    selectCollection(collection) {
      this.collection = collection
      this.select(collection)
    },

    async deleteItem(item_id) {
      this.loading_ = true

      try {
        await this.request('media.jellyfin.delete_item', {
          item_id: item_id,
        })
      } finally {
        this.loading_ = false
      }

      if (this.path.length > 1) {
        if (this.path[this.path.length - 1].id === item_id) {
          this.selectCollection(this.path[this.path.length - 2])
        }
      } else {
        this.collection = null
        this.select(this.rootItem)
      }
    },
  },

  watch: {
    collection() {
      this.setUrlArgs({ collection: this.collection?.id })
    },
  },

  mounted() {
    this.path = [this.rootItem]
  },

  unmounted() {
    this.setUrlArgs({ collection: null })
  },
}
</script>

<style lang="scss" scoped>
@import "../style.scss";

.media-jellyfin-container {
  height: 100%;

  .media-jellyfin-browser {
    height: calc(100% - $media-nav-height - 2px);
  }
}
</style>

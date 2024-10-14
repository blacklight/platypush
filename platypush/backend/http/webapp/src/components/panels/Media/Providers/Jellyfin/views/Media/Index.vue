<template>
  <div class="videos index">
    <Loading v-if="isLoading" />

    <div class="wrapper music-wrapper" v-else-if="collection?.collection_type === 'music'">
      <Music :collection="collection"
             :filter="filter"
             :loading="isLoading"
             :path="path"
             @play="$emit('play', $event)"
             @play-with-opts="$emit('play-with-opts', $event)"
             @select="selectedResult = $event; $emit('select', $event)"
             @select-collection="selectCollection" />
    </div>

    <NoItems :with-shadow="false"
             v-else-if="!items?.length">
      No videos found.
    </NoItems>

    <div class="wrapper items-wrapper" v-else>
      <Collections :collection="collection"
                   :filter="filter"
                   :items="collections"
                   :loading="isLoading"
                   :parent-id="collection?.id"
                   @select="selectCollection"
                   v-if="collections.length > 0" />

      <Results :results="mediaItems"
               :sources="{'jellyfin': true}"
               :filter="filter"
               :selected-result="selectedResult"
               @add-to-playlist="$emit('add-to-playlist', $event)"
               @download="$emit('download', $event)"
               @play="$emit('play', $event)"
               @play-with-opts="$emit('play-with-opts', $event)"
               @remove-from-playlist="$emit('remove-from-playlist', $event)"
               @select="selectedResult = $event"
               v-if="mediaItems.length > 0" />
    </div>
  </div>
</template>

<script>
import Collections from "@/components/panels/Media/Providers/Jellyfin/Collections";
import Loading from "@/components/Loading";
import Mixin from "@/components/panels/Media/Providers/Jellyfin/Mixin";
import Music from "../Music/Index";
import NoItems from "@/components/elements/NoItems";
import Results from "@/components/panels/Media/Results";

export default {
  mixins: [Mixin],
  emits: ['select', 'select-collection'],
  components: {
    Collections,
    Loading,
    Music,
    NoItems,
    Results,
  },

  computed: {
    collections() {
      return this.sortedItems?.filter((item) => item.item_type === 'collection') ?? []
    },

    mediaItems() {
      return this.sortedItems?.filter((item) => item.item_type !== 'collection') ?? []
    },
  },

  methods: {
    selectCollection(collection) {
      this.$emit('select-collection', {
        type: 'homevideos',
        ...collection,
      })
    },

    async init() {
      const args = this.getUrlArgs()
      let collection = args?.collection
      if (!collection)
        return

      this.loading_ = true
      try {
        collection = await this.request('media.jellyfin.info', {
          item_id: collection,
        })

        if (collection)
          this.selectCollection(collection)
      } finally {
        this.loading_ = false
      }
    },

    async refresh() {
      // Don't fetch items if we're in the music view -
      // we'll fetch them in the Music component
      if (this.collection?.collection_type === 'music')
        return

      this.loading_ = true
      try {
        if (this.collection?.collection_type === 'tvshows') {
          this.items = (
            await this.request('media.jellyfin.get_collections', {
              parent_id: this.collection.id,
            })
          ).map((collection) => ({
            ...collection,
            item_type: 'collection',
          }))
        } else {
          this.items = this.collection?.id ?
            (
              await this.request('media.jellyfin.get_items', {
                parent_id: this.collection.id,
                limit: 5000,
              })
            ) : (await this.request('media.jellyfin.get_collections')).map((collection) => ({
              ...collection,
              item_type: 'collection',
            }))
        }
      } finally {
        this.loading_ = false
      }
    },
  },

  async mounted() {
    this.init()
    await this.refresh()
  },
}
</script>

<style lang="scss" scoped>
@import "@/components/panels/Media/Providers/Jellyfin/common.scss";

.index {
  position: relative;

  :deep(.items-wrapper) {
    height: 100%;
    position: relative;
    overflow: auto;

    .index {
      height: fit-content;
    }

    .items {
      overflow: hidden;
    }
  }

  .music-wrapper {
    height: 100%;
  }
}
</style>

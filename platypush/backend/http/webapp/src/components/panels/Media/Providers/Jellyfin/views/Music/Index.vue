<template>
  <div class="music index">
    <Loading v-if="isLoading" />

    <NoItems :with-shadow="false" v-else-if="!items?.length">
      No music found.
    </NoItems>

    <main :class="{ album: view === 'album', artist: view === 'artist' }" v-else>
      <div class="artist header" v-if="view === 'artist'">
        <div class="image" v-if="collection.image">
          <img :src="collection.image" />
        </div>

        <div class="info">
          <h1 v-text="collection.name" />
        </div>
      </div>

      <div class="album header" v-if="view === 'album'">
        <div class="image" v-if="collection.image">
          <img :src="collection.image" />
        </div>

        <div class="info">
          <h1 v-text="collection.name" />
          <div class="artist" v-if="displayedArtist?.id">
            <a href="#" v-text="displayedArtist.name"
                        @click.prevent.stop="selectArtist"
                        v-if="displayedArtist" />
            <span v-text="displayedArtist.name" v-else />
          </div>
          <div class="details">
            <div class="row" v-if="collection.year">
              <span class="label">Year:</span>
              <span class="value" v-text="collection.year" />
            </div>

            <div class="row" v-if="collection.duration">
              <span class="label">Duration:</span>
              <span class="value" v-text="formatDuration(collection.duration, true)" />
            </div>
          </div>
        </div>
      </div>

      <Collections :collection="collection"
                   :filter="filter"
                   :items="collections"
                   :loading="isLoading"
                   :parent-id="collection?.id"
                   @select="selectCollection"
                   v-if="collections?.length > 0" />

      <Results :results="mediaItems"
               :sources="{'jellyfin': true}"
               :filter="filter"
               :list-view="true"
               :selected-result="selectedResult"
               :show-date="false"
               @add-to-playlist="$emit('add-to-playlist', $event)"
               @download="$emit('download', $event)"
               @play="$emit('play', $event)"
               @play-with-opts="$emit('play-with-opts', $event)"
               @remove-from-playlist="$emit('remove-from-playlist', $event)"
               @select="selectedResult = $event"
               v-if="mediaItems?.length > 0" />
    </main>
  </div>
</template>

<script>
import Collections from "@/components/panels/Media/Providers/Jellyfin/Collections";
import Loading from "@/components/Loading";
import Mixin from "@/components/panels/Media/Providers/Jellyfin/Mixin";
import NoItems from "@/components/elements/NoItems";
import Results from "@/components/panels/Media/Results";

export default {
  mixins: [Mixin],
  emits: ['select', 'select-collection'],
  components: {
    Collections,
    Loading,
    NoItems,
    Results,
  },

  data() {
    return {
      artist: null,
    }
  },

  computed: {
    collections() {
      return (
        this.sortedItems?.filter((item) => ['collection', 'artist', 'album'].includes(item.item_type)) ?? []
      ).sort((a, b) => a.name.localeCompare(b.name))
    },

    displayedArtist() {
      return this.artist || this.collection?.artist
    },

    mediaItems() {
      return (
        this.sortedItems?.filter((item) => !['collection', 'artist', 'album'].includes(item.item_type)) ?? []
      ).sort((a, b) => {
        if (this.view === 'album') {
          if (a.track_number && b.track_number) {
            if (a.track_number !== b.track_number) {
              return a.track_number - b.track_number
            }
          }
        }

        return a.name.localeCompare(b.name)
      }).map((item) => {
        if (this.view === 'album') {
          item.artist = this.artist || this.collection.artist
          item.album = this.collection
          item.image = this.collection.image
        }

        return item
      })
    },

    view() {
      switch (this.collection?.item_type) {
        case 'artist':
          return 'artist'
        case 'album':
          return 'album'
        default:
          return 'index'
      }
    },
  },

  methods: {
    async selectArtist() {
      const artistId = this.displayedArtist?.id || this.getUrlArgs().artist
      if (!artistId?.length)
        return

      this.loading_ = true
      try {
        const artist = this.displayedArtist || (await this.request('media.jellyfin.info', { item_id: artistId }))
        if (artist) {
          this.selectCollection(artist)
          this.$nextTick(() => {
            this.setUrlArgs({ artist: artist.id, collection: artist.id })
          })
        }
      } finally {
        this.loading_ = false
      }
    },

    selectCollection(collection) {
      if (!collection || collection?.id === this.collection?.id)
        return

      if (collection.item_type === 'artist') {
        this.setUrlArgs({ artist: collection.id })
      } else if (collection.item_type === 'album') {
        this.setUrlArgs({ collection: collection.id })
      } else {
        this.setUrlArgs({ collection: null })
      }

      this.$emit('select-collection', {
        collection_type: 'music',
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
      this.loading_ = true
      try {
        switch (this.view) {
          case 'artist':
            this.artist = {...this.collection}
            this.setUrlArgs({
              artist: this.collection.id,
              collection: this.collection.id,
            })

            this.items = (
              await this.request(
                'media.jellyfin.get_items',
                {
                  parent_id: this.collection.id,
                  limit: 25000,
                }
              )
            ).map((item) => {
              if (this.collection?.item_type === 'album') {
                item.image = this.collection.image
              }

              return item
            })
            break

          case 'album':
            this.setUrlArgs({
              collection: this.collection.id,
              artist: this.collection.artist?.id,
            })

            this.items = await this.request(
              'media.jellyfin.get_items',
              {
                parent_id: this.collection.id,
                limit: 25000,
              }
            )
            break

          default:
            this.artist = null
            this.items = await this.request(
              'media.jellyfin.get_artists',
              { limit: 5000 }
            )
            break
        }
      } finally {
        this.loading_ = false
      }
    },
  },

  async mounted() {
    await this.init()
    await this.refresh()
  },

  unmounted() {
    this.setUrlArgs({
      collection: null,
      artist: null,
      album: null,
    })
  },
}
</script>

<style lang="scss" scoped>
@import "@/components/panels/Media/Providers/Jellyfin/common.scss";

$artist-header-height: 5em;
$album-header-height: 10em;

.index {
  position: relative;

  :deep(main) {
    height: 100%;
    position: relative;
    overflow: auto;

    &.artist, &.album {
      overflow: hidden;

      .media-results {
        overflow: auto;

        .grid {
          height: fit-content;
          max-height: 100%;
        }
      }
    }

    &.artist {
      .index {
        height: 100%;

        .items {
          height: calc(100% - #{$artist-header-height} - 0.5em);
          overflow: auto;
        }
      }
    }

    &.album {
      .media-results {
        height: calc(100% - #{$album-header-height} - 0.5em);
      }
    }

    .index {
      height: fit-content;
    }

    .items {
      overflow: hidden;
    }
  }

  .header {
    background: $info-header-bg;
    display: flex;
    align-items: center;
    padding: 1em;
    box-shadow: $border-shadow-bottom;
    margin-bottom: 0.5em;
    position: relative;

    &.artist {
      height: $artist-header-height;
      padding: 0;
      background: linear-gradient(rgba(0, 20, 25, 0.85), rgba(0, 0, 0, 0.85));
      color: white;

      .image {
        width: $artist-header-height;
        height: $artist-header-height;

        img {
          width: 100%;
          height: 95%;
        }
      }

      .info {
        font-size: 1.25em;
      }
    }

    &.album {
      height: $album-header-height;

      .image {
        img {
          width: $album-header-height;
          height: $album-header-height;
        }
      }
    }

    .image {
      margin-right: 1em;

      img {
        object-fit: cover;
        margin: 0.25em;
      }
    }

    .info {
      h1 {
        font-size: 1.5em;
        margin: 0;
      }

      span {
        font-size: 1.25em;
      }

      .artist {
        a {
          font-size: 1.25em;
        }
      }

      .details {
        font-size: 0.7em;
        margin-top: 0.5em;
        opacity: 0.75;

        .row {
          .label {
            font-weight: bold;
            margin-right: 0.5em;
          }
        }
      }
    }
  }

  :deep(.media-results.list ) {
    .grid {
      margin-top: -0.5em;
    }
  }
}
</style>

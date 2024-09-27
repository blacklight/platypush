<template>
  <div class="movies index">
    <Loading v-if="isLoading" />

    <NoItems :with-shadow="false"
             v-else-if="sortedMovies.length === 0">
      No movies found.
    </NoItems>

    <Results :results="sortedMovies"
             :sources="{'jellyfin': true}"
             :filter="filter"
             :selected-result="selectedResult"
             @add-to-playlist="$emit('add-to-playlist', $event)"
             @download="$emit('download', $event)"
             @play="$emit('play', $event)"
             @play-with-opts="$emit('play-with-opts', $event)"
             @remove-from-playlist="$emit('remove-from-playlist', $event)"
             @select="selectedResult = $event"
             v-else />
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import MediaProvider from "@/components/panels/Media/Providers/Mixin";
import NoItems from "@/components/elements/NoItems";
import Results from "@/components/panels/Media/Results";

export default {
  mixins: [MediaProvider],
  components: {
    Loading,
    NoItems,
    Results,
  },

  emits: [
    'add-to-playlist',
    'back',
    'download',
    'play',
    'play-with-opts',
  ],

  props: {
    collection: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      movies: {},
      loading_: false,
      selectedResult: null,
    };
  },

  computed: {
    isLoading() {
      return this.loading_ || this.loading
    },

    sortedMovies() {
      return [...this.movies].sort((a, b) => {
        return a.title.localeCompare(b.title)
      }).map((movie) => {
        return {
          item_type: movie.type,
          ...movie,
          type: 'jellyfin',
        }
      })
    },
  },

  methods: {
    async refresh() {
      const collection = this.collection?.name
      if (!collection?.length) {
        return
      }

      this.loading_ = true
      try {
        this.movies = await this.request(
          'media.jellyfin.search',
          { collection, limit: 1000 },
        )

      } finally {
        this.loading_ = false
      }
    },
  },

  watch: {
    collection: {
      immediate: true,
      handler() {
        this.refresh()
      },
    },
  },

  async mounted() {
    await this.refresh()
  },
}
</script>

<style lang="scss" scoped>
@import "@/components/panels/Media/Providers/Jellyfin/common.scss";
</style>

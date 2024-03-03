<template>
  <div class="media-youtube-playlist">
    <Loading v-if="loading" />
    <NoItems :with-shadow="false" v-else-if="!items?.length">
      No videos found.
    </NoItems>

    <Results :results="items"
             :sources="{'youtube': true}"
             :filter="filter"
             :selected-result="selectedResult"
             @select="selectedResult = $event"
             @play="$emit('play', $event)"
             v-else />
  </div>
</template>

<script>
import NoItems from "@/components/elements/NoItems";
import Loading from "@/components/Loading";
import Results from "@/components/panels/Media/Results";
import Utils from "@/Utils";

export default {
  emits: ['play'],
  mixins: [Utils],
  components: {
    Loading,
    NoItems,
    Results,
  },

  props: {
    id: {
      type: String,
      required: true,
    },

    filter: {
      type: String,
      default: null,
    },
  },

  data() {
    return {
      items: [],
      loading: false,
      selectedResult: null,
    }
  },

  methods: {
    async loadItems() {
      this.loading = true
      try {
        this.items = (
          await this.request('youtube.get_playlist', {id: this.id})
        ).map(item => ({
          ...item,
          type: 'youtube',
        }))
      } finally {
        this.loading = false
      }
    },
  },

  mounted() {
    this.loadItems()
  },
}
</script>

<style lang="scss" scoped>
.media-youtube-playlist {
  height: 100%;
}
</style>

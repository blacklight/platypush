<template>
  <div class="media-youtube-feed">
    <Loading v-if="loading" />
    <NoItems :with-shadow="false" v-else-if="!feed?.length">
      No videos found.
    </NoItems>

    <Results :results="feed"
             :filter="filter"
             :sources="{'youtube': true}"
             :selected-result="selectedResult"
             @add-to-playlist="$emit('add-to-playlist', $event)"
             @download="$emit('download', $event)"
             @open-channel="$emit('open-channel', $event)"
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
  mixins: [Utils],
  emits: [
    'add-to-playlist',
    'download',
    'open-channel',
    'play',
  ],

  components: {
    Loading,
    NoItems,
    Results,
  },

  props: {
    filter: {
      type: String,
      default: null,
    },
  },

  data() {
    return {
      feed: [],
      loading: false,
      selectedResult: null,
    }
  },

  methods: {
    async loadFeed() {
      this.loading = true
      try {
        this.feed = (await this.request('youtube.get_feed')).map(item => ({
          ...item,
          type: 'youtube',
        }))
      } finally {
        this.loading = false
      }
    },
  },

  mounted() {
    this.loadFeed()
  },
}
</script>

<style lang="scss" scoped>
.media-youtube-feed {
  height: 100%;
}
</style>

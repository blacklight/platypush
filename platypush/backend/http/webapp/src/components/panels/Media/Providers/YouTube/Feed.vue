<template>
  <div class="media-youtube-feed">
    <Loading v-if="isLoading" />
    <NoItems :with-shadow="false" v-else-if="!feed?.length">
      No videos found.
    </NoItems>

    <Results :results="feed"
             :filter="filter"
             :sources="{'youtube': true}"
             :selected-result="selectedResult"
             @add-to-playlist="$emit('add-to-playlist', $event)"
             @download="$emit('download', $event)"
             @download-audio="$emit('download-audio', $event)"
             @open-channel="$emit('open-channel', $event)"
             @select="selectedResult = $event"
             @play="$emit('play', $event)"
             @play-with-opts="$emit('play-with-opts', $event)"
             @scroll-end="loadFeed"
             @view="$emit('view', $event)"
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
    'download-audio',
    'open-channel',
    'play',
    'play-with-opts',
    'view',
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

    loading: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      feed: [],
      firstLoad: true,
      loading_: false,
      page: 1,
      selectedResult: null,
    }
  },

  computed: {
    isLoading() {
      return (this.loading_ || this.loading) && this.firstLoad
    },
  },

  methods: {
    async loadFeed() {
      this.loading_ = true
      try {
        this.feed.push(
          ...(
            await this.request('youtube.get_feed', {
              page: this.page,
            })
          ).map(item => ({
            ...item,
            type: 'youtube',
          }))
        )

        this.firstLoad = false
        if (this.feed.length) {
          this.page++
        }
      } finally {
        this.loading_ = false
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

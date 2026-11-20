<template>
  <div class="media-youtube-feed">
    <Loading v-if="isLoading" />
    <NoItems :with-shadow="false" v-else-if="!visibleFeed?.length">
      No videos found.
    </NoItems>

    <div class="feed-options" v-if="feed?.length">
      <label>
        <input type="checkbox" v-model="hideStories" />
        Hide stories
      </label>
    </div>

    <Results :results="visibleFeed"
             :filter="filter"
             :sources="{'youtube': true}"
             :selected-result="selectedResult"
             @add-to-playlist="$emit('add-to-playlist', $event)"
             @add-to-queue="$emit('add-to-queue', $event)"
             @download="$emit('download', $event)"
             @download-audio="$emit('download-audio', $event)"
             @open-channel="$emit('open-channel', $event)"
             @select="selectedResult = $event"
             @play="$emit('play', $event)"
             @play-with-opts="$emit('play-with-opts', $event)"
             @scroll-end="loadFeed"
             @view="$emit('view', $event)" />
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
    'add-to-queue',
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
      hideStories: true,
      loading_: false,
      nextPageToken: 1,
      renderedPageTokens: {},
      selectedResult: null,
    }
  },

  computed: {
    isLoading() {
      return (this.loading_ || this.loading) && this.firstLoad
    },

    visibleFeed() {
      if (!this.hideStories)
        return this.feed

      return this.feed.filter(item => (item.duration || 0) > 0)
    },
  },

  methods: {
    async loadFeed() {
      if (this.loading_ || this.nextPageToken == null) {
        return
      }

      // Don't load the same page twice
      if (this.renderedPageTokens[this.nextPageToken]) {
        return
      }

      this.loading_ = true
      try {
        const items = (await this.request('youtube.get_feed', {
          page: this.nextPageToken,
        })).map(item => ({
          ...item,
          type: 'youtube',
        }))

        const knownIds = new Set(this.feed.map(item => item.id))
        const newItems = items.filter(item => !knownIds.has(item.id))
        this.feed.push(...newItems)

        this.firstLoad = false
        this.renderedPageTokens[this.nextPageToken] = true

        if (items.length && newItems.length) {
          this.nextPageToken = items[items.length - 1].next_page_token
        } else {
          this.nextPageToken = null
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

  .feed-options {
    display: flex;
    justify-content: flex-end;
    padding: 0.5em;

    label {
      display: inline-flex;
      align-items: center;
      cursor: pointer;

      input {
        margin-right: 0.5em;
      }
    }
  }
}
</style>

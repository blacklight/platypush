<template>
  <div class="media-youtube-channel" @scroll="onScroll">
    <Loading v-if="loading" />

    <div class="channel" @scroll="onScroll" v-else-if="channel">
      <div class="header">
        <div class="banner">
          <img :src="channel.banner" v-if="channel?.banner?.length" />
        </div>

        <div class="row info-container">
          <div class="info">
            <div class="row">
              <a :href="channel.url" target="_blank" rel="noopener noreferrer" v-if="channel?.image?.length">
                <div class="image">
                  <img :src="channel.image" />
                </div>
              </a>

              <a class="title" :href="channel.url" target="_blank" rel="noopener noreferrer">
                {{ channel?.name }}
              </a>
            </div>

            <div class="description" v-if="channel?.description">
              {{ channel.description }}
            </div>
          </div>
        </div>
      </div>

      <Results :results="channel.items"
               :filter="filter"
               :selected-result="selectedResult"
               ref="results"
               @select="selectedResult = $event"
               @play="$emit('play', $event)" />
    </div>
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import Results from "@/components/panels/Media/Results";
import Utils from "@/Utils";

export default {
  emits: ['play'],
  mixins: [Utils],
  components: {
    Loading,
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
      channel: null,
      loading: false,
      loadingNextPage: false,
      selectedResult: null,
    }
  },

  computed: {
    itemsByUrl() {
      return this.channel?.items.reduce((acc, item) => {
        acc[item.url] = item
        return acc
      }, {})
    },
  },

  methods: {
    async loadChannel() {
      this.loading = true
      try {
        this.channel = await this.request('youtube.get_channel', {id: this.id})
      } finally {
        this.loading = false
      }
    },

    async loadNextPage() {
      if (!this.channel?.next_page_token || this.loadingNextPage)
        return

      try {
        const nextPage = await this.request(
          'youtube.get_channel',
          {id: this.id, next_page_token: this.channel.next_page_token}
        )

        this.channel.items.push(...nextPage.items.filter(item => !this.itemsByUrl[item.url]))
        this.channel.next_page_token = nextPage.next_page_token
        this.$refs.results.maxResultIndex += this.$refs.results.resultIndexStep
      } finally {
        this.loadingNextPage = false
      }
    },

    onScroll(e) {
      const el = e.target
      if (!el)
        return

      const bottom = (el.scrollHeight - el.scrollTop) <= el.clientHeight + 150
      if (!bottom)
        return

      this.loadNextPage()
    },
  },

  mounted() {
    this.loadChannel()
  },
}
</script>

<style lang="scss" scoped>
@import "header.scss";

.media-youtube-channel {
  height: 100%;
  overflow-y: auto;

  .channel {
    height: 100%;
  }
}
</style>

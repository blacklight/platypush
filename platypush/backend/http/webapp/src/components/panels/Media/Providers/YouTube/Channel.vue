<template>
  <div class="media-youtube-channel">
    <Loading v-if="loading" />

    <div class="channel" v-else-if="channel">
      <div class="header">
        <div class="banner">
          <img :src="channel.banner" v-if="channel?.banner?.length" />
        </div>

        <div class="row info-container">
          <div class="info">
            <div class="row">
              <div class="title-container">
                <a :href="channel.url" target="_blank" rel="noopener noreferrer" v-if="channel?.image?.length">
                  <div class="image">
                    <img :src="channel.image" />
                  </div>
                </a>

                <a class="title" :href="channel.url" target="_blank" rel="noopener noreferrer">
                  {{ channel?.name }}
                </a>
              </div>

              <div class="actions">
                <button :title="subscribed ? 'Unsubscribe' : 'Subscribe'" @click="toggleSubscription">
                  {{ subscribed ? 'Unsubscribe' : 'Subscribe' }}
                </button>

                <div class="subscribers" v-if="channel.subscribers != null && (channel.subscribers || 0) >= 0">
                  {{ channel.subscribers }} subscribers
                </div>
              </div>
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
               @download="$emit('download', $event)"
               @play="$emit('play', $event)"
               @scroll-end="loadNextPage"
               @select="selectedResult = $event"
      />
    </div>
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import Results from "@/components/panels/Media/Results";
import Utils from "@/Utils";

export default {
  emits: ['download', 'play'],
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
      subscribed: false,
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
        this.subscribed = await this.request('youtube.is_subscribed', {channel_id: this.id})
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

    async toggleSubscription() {
      const action = this.subscribed ? 'unsubscribe' : 'subscribe'
      await this.request(`youtube.${action}`, {channel_id: this.id})
      this.subscribed = !this.subscribed
    },

    onScroll(e) {
      const el = e.target
      if (!el)
        return

      const bottom = (el.scrollHeight - el.scrollTop) <= el.clientHeight + 100
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

  .header {
    .title-container {
      flex: 1;
    }

    .actions {
      display: flex;
      flex-direction: column;
      align-items: center;

      button {
        background: $default-bg-7;
        padding: 0.5em 1em;
        border-radius: 0.5em;
        cursor: pointer;

        &:hover {
          background: $hover-bg;
        }
      }
    }

    .subscribers {
      font-size: 0.8em;
    }
  }
}
</style>

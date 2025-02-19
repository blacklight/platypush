<template>
  <div class="media-youtube-channel">
    <Loading v-if="isLoading" />

    <div class="channel" v-else-if="channel">
      <div class="header">
        <div class="banner">
          <img :src="channel.banner" @error="onBannerError" v-if="banner?.length" />
        </div>

        <div class="row info-container">
          <div class="info">
            <div class="row">
              <div class="title-container">
                <a :href="channel.url" target="_blank" rel="noopener noreferrer" v-if="image?.length">
                  <div class="image">
                    <img :src="image" @error="onImageError" />
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
                  {{ formatNumber(channel.subscribers) }} subscribers
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row description-container" v-if="channel?.description">
        <div class="description-toggle">
          <button :title="showDescription ? 'Hide description' : 'Show description'"
                  @click="showDescription = !showDescription">
            <i class="fas" :class="{'fa-chevron-down': !showDescription, 'fa-chevron-up': showDescription}"></i>
          </button>
        </div>

        <div class="description" :class="{hidden: !showDescription}" v-if="channel?.description">
          {{ channel.description }}
        </div>
      </div>

      <Results :results="channel.items"
               :filter="filter"
               :result-index-step="null"
               :selected-result="selectedResult"
               ref="results"
               @add-to-playlist="$emit('add-to-playlist', $event)"
               @download="$emit('download', $event)"
               @download-audio="$emit('download-audio', $event)"
               @open-channel="$emit('open-channel', $event)"
               @play="$emit('play', $event)"
               @play-with-opts="$emit('play-with-opts', $event)"
               @scroll-end="loadNextPage"
               @select="selectedResult = $event"
               @view="$emit('view', $event)"
      />
    </div>
  </div>
</template>

<script>
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

    loading: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      banner: null,
      channel: null,
      image: null,
      loading_: false,
      loadingNextPage: false,
      nextPageToken: null,
      renderedPageTokens: {},
      selectedResult: null,
      showDescription: false,
      subscribed: false,
    }
  },

  computed: {
    isLoading() {
      return this.loading || this.loading_
    },

    itemsByUrl() {
      return this.channel?.items.reduce((acc, item) => {
        acc[item.url] = item
        return acc
      }, {})
    },
  },

  methods: {
    async loadChannel() {
      this.loading_ = true
      try {
        await this.updateChannel(true)
        this.subscribed = await this.request('youtube.is_subscribed', {channel_id: this.id})
      } finally {
        this.loading_ = false
      }
    },

    async updateChannel(init) {
      const nextPageToken = this.channel?.next_page_token
      const channel = await this.request(
        'youtube.get_channel',
        {id: this.id, page: nextPageToken}
      )

      if (nextPageToken) {
        this.renderedPageTokens[nextPageToken] = true
      }

      this.nextPageToken = channel.next_page_token
      this.image = channel.image
      this.banner = channel.banner

      const itemsByUrl = this.itemsByUrl || {}
      let items = channel.items
        .filter(item => !itemsByUrl[item.url])
        .map(item => {
          return {
            type: 'youtube',
            ...item,
          }
        })

      if (!init) {
        items = this.channel.items.concat(items)
      }

      this.channel = channel
      this.channel.items = items
    },

    async loadNextPage() {
      if (!this.nextPageToken || this.renderedPageTokens[this.nextPageToken] || this.loadingNextPage) {
        return
      }

      this.loadingNextPage = true

      try {
        await this.timeout(500)
        await this.updateChannel()
      } finally {
        this.loadingNextPage = false
      }
    },

    async toggleSubscription() {
      const action = this.subscribed ? 'unsubscribe' : 'subscribe'
      await this.request(`youtube.${action}`, {channel_id: this.id})
      this.subscribed = !this.subscribed
    },

    onBannerError() {
      this.banner = null
    },

    onImageError() {
      this.image = null
    },
  },

  async mounted() {
    this.setUrlArgs({channel: this.id})
    await this.loadChannel()
  },

  unmounted() {
    this.setUrlArgs({channel: null})
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
    position: relative;
  }

  .header {
    .title-container {
      flex: 1;
    }

    .actions {
      display: flex;
      flex-direction: column;
      align-items: flex-end;

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

<template>
  <div class="media-info">
    <Loading v-if="loading" />

    <div class="row header">
      <div class="item-container">
        <Item :item="item"
              @add-to-playlist="$emit('add-to-playlist', item)"
              @open-channel="$emit('open-channel', item)"
              @play="$emit('play', item)"
              @play-with-opts="$emit('play-with-opts', $event)"
              @download="$emit('download', item)"
              @download-audio="$emit('download-audio', item)"
        />
      </div>
    </div>

    <div class="row direct-url" v-if="mainUrl">
      <div class="left side">Direct URL</div>
      <div class="right side">
        <a :href="mainUrl" title="Direct URL" target="_blank">
          <i class="fas fa-external-link-alt" />
        </a>
        <button @click="copyToClipboard(mainUrl)" title="Copy URL to clipboard">
          <i class="fas fa-clipboard" />
        </button>
      </div>
    </div>

    <div class="row direct-url" v-if="computedItem?.imdb_url">
      <div class="left side">ImDB URL</div>
      <div class="right side">
        <a :href="computedItem.imdb_url" title="ImDB URL" target="_blank">
          <i class="fas fa-external-link-alt" />
        </a>
        <button @click="copyToClipboard(computedItem.imdb_url)" title="Copy URL to clipboard">
          <i class="fas fa-clipboard" />
        </button>
      </div>
    </div>

    <div class="row" v-if="computedItem?.artist?.name">
      <div class="left side">Artist</div>
      <div class="right side" v-text="computedItem.artist.name" />
    </div>

    <div class="row" v-if="computedItem?.album?.name">
      <div class="left side">Album</div>
      <div class="right side" v-text="computedItem.album.name" />
    </div>

    <div class="row" v-if="computedItem?.series">
      <div class="left side">TV Series</div>
      <div class="right side" v-text="computedItem.series" />
    </div>

    <div class="row" v-if="computedItem?.season">
      <div class="left side">Season</div>
      <div class="right side" v-text="computedItem.season" />
    </div>

    <div class="row" v-if="computedItem?.episode">
      <div class="left side">Episode</div>
      <div class="right side" v-text="computedItem.episode" />
    </div>

    <div class="row" v-if="computedItem?.num_seasons">
      <div class="left side">Number of seasons</div>
      <div class="right side" v-text="computedItem.num_seasons" />
    </div>

    <div class="row" v-if="computedItem?.description">
      <div class="left side">Description</div>
      <div class="right side" v-text="computedItem.description" />
    </div>

    <div class="row" v-if="computedItem?.summary">
      <div class="left side">Summary</div>
      <div class="right side" v-text="computedItem.summary" />
    </div>

    <div class="row" v-if="computedItem?.overview">
      <div class="left side">Overview</div>
      <div class="right side" v-text="computedItem.overview" />
    </div>

    <div class="row" v-if="computedItem?.country">
      <div class="left side">Country</div>
      <div class="right side" v-text="computedItem.country" />
    </div>

    <div class="row" v-if="computedItem?.network">
      <div class="left side">Network</div>
      <div class="right side" v-text="computedItem.network" />
    </div>

    <div class="row" v-if="computedItem?.status">
      <div class="left side">Status</div>
      <div class="right side" v-text="computedItem.status" />
    </div>

    <div class="row" v-if="computedItem?.width && computedItem?.height">
      <div class="left side">Resolution</div>
      <div class="right side">
        {{ computedItem.width }}x{{ computedItem.height }}
      </div>
    </div>

    <div class="row" v-if="computedItem?.view_count != null">
      <div class="left side">Views</div>
      <div class="right side">{{ formatNumber(computedItem.view_count) }}</div>
    </div>

    <div class="row" v-if="computedItem?.rating">
      <div class="left side">Rating</div>
      <div class="right side">{{ Math.round(computedItem.rating) }}%</div>
    </div>

    <div class="row" v-if="computedItem?.critic_rating">
      <div class="left side">Critic Rating</div>
      <div class="right side">{{ Math.round(computedItem.critic_rating) }}%</div>
    </div>

    <div class="row" v-if="computedItem?.community_rating">
      <div class="left side">Community Rating</div>
      <div class="right side">{{ Math.round(computedItem.community_rating) }}%</div>
    </div>

    <div class="row" v-if="computedItem?.votes">
      <div class="left side">Votes</div>
      <div class="right side" v-text="computedItem.votes" />
    </div>

    <div class="row" v-if="computedItem?.genres">
      <div class="left side">Genres</div>
      <div class="right side" v-text="computedItem.genres.join(', ')" />
    </div>

    <div class="row" v-if="channel">
      <div class="left side">Channel</div>
      <div class="right side">
        <a :href="channel.url" target="_blank" v-text="channel.title || channel.url" />
      </div>
    </div>

    <div class="row" v-if="computedItem?.year">
      <div class="left side">Year</div>
      <div class="right side" v-text="computedItem.year" />
    </div>

    <div class="row" v-if="publishedDate">
      <div class="left side">Published at</div>
      <div class="right side" v-text="publishedDate" />
    </div>

    <div class="row" v-if="computedItem?.file">
      <div class="left side">File</div>
      <div class="right side" v-text="computedItem.file" />
    </div>

    <div class="row" v-if="computedItem?.track_number != null">
      <div class="left side">Track</div>
      <div class="right side" v-text="computedItem.track_number" />
    </div>

    <div class="row" v-if="computedItem?.trailer">
      <div class="left side">Trailer</div>
      <div class="right side url">
        <a :href="computedItem.trailer" target="_blank" v-text="computedItem.trailer" />
      </div>
    </div>

    <div class="row" v-if="computedItem?.size">
      <div class="left side">Size</div>
      <div class="right side" v-text="convertSize(computedItem.size)" />
    </div>

    <div class="row" v-if="computedItem?.quality">
      <div class="left side">Quality</div>
      <div class="right side" v-text="computedItem.quality" />
    </div>

    <div class="row" v-if="computedItem?.seeds">
      <div class="left side">Seeds</div>
      <div class="right side" v-text="computedItem.seeds" />
    </div>

    <div class="row" v-if="computedItem?.peers">
      <div class="left side">Peers</div>
      <div class="right side" v-text="computedItem.peers" />
    </div>

    <div class="row" v-if="computedItem?.tags">
      <div class="left side">Tags</div>
      <div class="right side" v-text="computedItem.tags.join(', ')" />
    </div>

    <div class="row" v-if="computedItem?.language">
      <div class="left side">Language</div>
      <div class="right side" v-text="computedItem.language" />
    </div>

    <div class="row" v-if="computedItem?.audio_channels">
      <div class="left side">Audio Channels</div>
      <div class="right side" v-text="computedItem.audio_channels" />
    </div>
  </div>
</template>

<script>
import Icons from "./icons.json";
import Item from "./Item";
import Loading from "@/components/Loading";
import MediaUtils from "@/components/Media/Utils";
import Utils from "@/Utils";

export default {
  name: "Info",
  components: {
    Item,
    Loading,
  },
  mixins: [Utils, MediaUtils],
  emits: [
    'add-to-playlist',
    'download',
    'download-audio',
    'open-channel',
    'play',
    'play-with-opts',
  ],
  props: {
    item: {
      type: Object,
      default: () => {},
    },

    pluginName: {
      type: String,
    },
  },

  data() {
    return {
      typeIcons: Icons,
      loading: false,
      loadingUrl: false,
      youtubeUrl: null,
      metadata: null,
    }
  },

  computed: {
    channel() {
      let ret = null
      if (this.item?.channelId)
        ret = {
          url: `https://www.youtube.com/channel/${this.item.channelId}`,
        }
      else if (this.item?.channel_url)
        ret = {
          url: this.item.channel_url,
        }

      if (!ret)
        return null

      if (this.item?.channelTitle)
        ret.title = this.item.channelTitle
      else if (this.item?.channel)
        ret.title = this.item.channel

      return ret
    },

    computedItem() {
      return {
        ...(this.item || {}),
        ...(this.metadata || {}),
      }
    },

    publishedDate() {
      if (this.item?.publishedAt)
        return this.formatDate(this.item.publishedAt, true)
      if (this.item?.created_at)
        return this.formatDate(this.item.created_at, true)
      if (this.item?.timestamp)
        return this.formatDate(this.item.timestamp, true)

      return null
    },

    directUrl() {
      if (this.item?.type === 'file' && this.item?.url) {
        const path = this.item.url.replace(/^file:\/\//, '')
        return window.location.origin + '/file?path=' + encodeURIComponent(path)
      }

      return null
    },

    mainUrl() {
      const directUrl = this.directUrl
      if (directUrl)
        return directUrl

      return this.item?.url
    },
  },

  methods: {
    async updateMetadata() {
      this.loading = true

      try {
        if (this.item?.type === 'jellyfin' && this.item?.id) {
          this.metadata = await this.request('media.jellyfin.info', {
            item_id: this.item.id,
          })
        }
      } finally {
        this.loading = false
      }
    },
  },

  watch: {
    item: {
      handler() {
        this.updateMetadata()
      },
      deep: true,
    },
  },

  mounted() {
    this.updateMetadata()
  },
}
</script>

<style lang="scss" scoped>
@import "~@/components/Media/vars";

.media-info {
  width: 100%;
  max-width: 60em;
}

.row {
  display: flex;
  min-height: 3em;
  padding: .5em 1em;

  @include until ($tablet) {
    flex-direction: column;
  }

  @include from ($tablet) {
    align-items: center;
  }

  &:not(:last-child) {
    border-bottom: $default-border-2;
  }

  &:hover {
    background: $hover-bg;
    border-radius: .5em;
  }

  .side {
    align-items: center;
    display: inline-flex;

    &.url {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    @include until ($tablet) {
      display: flex;

      &.left {
        font-weight: bold;
      }

      &.right {
        justify-content: left;
      }
    }

    @include from ($tablet) {
      display: inline-flex;

      &.left {
        width: 22%;
        margin-right: 3%;
      }

      &.right {
        width: 75%;
        justify-content: right;
      }
    }
  }
}

.direct-url {
  .right.side {
    position: relative;

    button {
      background: none;
      border: none;
      padding: 0;
      margin-left: 1em;

      &:hover {
        color: $default-hover-fg;
        cursor: pointer;
      }
    }
  }
}

.header {
  width: 100%;
  display: flex;
  flex-direction: column;
  position: relative;

  .item-container {
    @include from($desktop) {
      width: 420px;
    }
  }

  .title {
    width: 100%;
    font-size: 1.5em;
    font-weight: bold;
    margin-top: 0.5em;
    text-align: center;
    overflow-wrap: break-word;

    @include from($desktop) {
      flex: 1;
      padding-left: 1em;
    }
  }

  &:hover {
    background: initial;
  }
}
</style>

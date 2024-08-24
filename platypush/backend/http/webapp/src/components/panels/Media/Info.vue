<template>
  <div class="media-info">
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

    <div class="row" v-if="item?.series">
      <div class="left side">TV Series</div>
      <div class="right side" v-text="item.series" />
    </div>

    <div class="row" v-if="item?.season">
      <div class="left side">Season</div>
      <div class="right side" v-text="item.season" />
    </div>

    <div class="row" v-if="item?.episode">
      <div class="left side">Episode</div>
      <div class="right side" v-text="item.episode" />
    </div>

    <div class="row" v-if="item?.num_seasons">
      <div class="left side">Number of seasons</div>
      <div class="right side" v-text="item.num_seasons" />
    </div>

    <div class="row" v-if="item?.description">
      <div class="left side">Description</div>
      <div class="right side" v-text="item.description" />
    </div>

    <div class="row" v-if="item?.summary">
      <div class="left side">Summary</div>
      <div class="right side" v-text="item.summary" />
    </div>

    <div class="row" v-if="item?.overview">
      <div class="left side">Overview</div>
      <div class="right side" v-text="item.overview" />
    </div>

    <div class="row" v-if="item?.country">
      <div class="left side">Country</div>
      <div class="right side" v-text="item.country" />
    </div>

    <div class="row" v-if="item?.network">
      <div class="left side">Network</div>
      <div class="right side" v-text="item.network" />
    </div>

    <div class="row" v-if="item?.status">
      <div class="left side">Status</div>
      <div class="right side" v-text="item.status" />
    </div>

    <div class="row" v-if="item?.width && item?.height">
      <div class="left side">Resolution</div>
      <div class="right side">
        {{ item.width }}x{{ item.height }}
      </div>
    </div>

    <div class="row" v-if="item?.view_count != null">
      <div class="left side">Views</div>
      <div class="right side">{{ formatNumber(item.view_count) }}</div>
    </div>

    <div class="row" v-if="item?.rating">
      <div class="left side">Rating</div>
      <div class="right side">{{ item.rating }}%</div>
    </div>

    <div class="row" v-if="item?.critic_rating">
      <div class="left side">Critic Rating</div>
      <div class="right side">{{ item.critic_rating }}%</div>
    </div>

    <div class="row" v-if="item?.community_rating">
      <div class="left side">Community Rating</div>
      <div class="right side">{{ item.community_rating }}%</div>
    </div>

    <div class="row" v-if="item?.votes">
      <div class="left side">Votes</div>
      <div class="right side" v-text="item.votes" />
    </div>

    <div class="row" v-if="item?.genres">
      <div class="left side">Genres</div>
      <div class="right side" v-text="item.genres.join(', ')" />
    </div>

    <div class="row" v-if="channel">
      <div class="left side">Channel</div>
      <div class="right side">
        <a :href="channel.url" target="_blank" v-text="channel.title || channel.url" />
      </div>
    </div>

    <div class="row" v-if="item?.year">
      <div class="left side">Year</div>
      <div class="right side" v-text="item.year" />
    </div>

    <div class="row" v-if="publishedDate">
      <div class="left side">Published at</div>
      <div class="right side" v-text="publishedDate" />
    </div>

    <div class="row" v-if="item?.file">
      <div class="left side">File</div>
      <div class="right side" v-text="item.file" />
    </div>

    <div class="row" v-if="item?.trailer">
      <div class="left side">Trailer</div>
      <div class="right side url">
        <a :href="item.trailer" target="_blank" v-text="item.trailer" />
      </div>
    </div>

    <div class="row" v-if="item?.size">
      <div class="left side">Size</div>
      <div class="right side" v-text="convertSize(item.size)" />
    </div>

    <div class="row" v-if="item?.quality">
      <div class="left side">Quality</div>
      <div class="right side" v-text="item.quality" />
    </div>

    <div class="row" v-if="item?.seeds">
      <div class="left side">Seeds</div>
      <div class="right side" v-text="item.seeds" />
    </div>

    <div class="row" v-if="item?.peers">
      <div class="left side">Peers</div>
      <div class="right side" v-text="item.peers" />
    </div>

    <div class="row" v-if="item?.language">
      <div class="left side">Language</div>
      <div class="right side" v-text="item.language" />
    </div>

    <div class="row" v-if="item?.audio_channels">
      <div class="left side">Audio Channels</div>
      <div class="right side" v-text="item.audio_channels" />
    </div>
  </div>
</template>

<script>
import Icons from "./icons.json";
import Item from "./Item";
import MediaUtils from "@/components/Media/Utils";
import Utils from "@/Utils";

export default {
  name: "Info",
  components: {
    Item,
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
      loadingUrl: false,
      youtubeUrl: null,
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
}
</script>

<style lang="scss" scoped>
@import "~@/components/Media/vars";

.media-info {
  width: 100%;
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

<template>
  <div class="media-youtube-subscriptions">
    <div class="subscriptions-index" v-if="!selectedChannel?.id" @scroll="onScroll">
      <Loading v-if="showLoading" />
      <NoItems :with-shadow="false" v-else-if="!channels?.length">
        No channels found.
      </NoItems>

      <div class="body grid" v-else>
        <div class="channel item"
             v-for="(channel, id) in channelsById"
             :key="id"
             @click="$emit('select', channel)">
          <div class="image">
            <img :src="channel.image" :alt="channel.name" />
          </div>
          <div class="title">{{ channel.name }}</div>
        </div>
      </div>
    </div>

    <div class="subscription-body" v-else>
      <Channel
        :id="selectedChannel.id"
        :filter="filter"
        @add-to-playlist="$emit('add-to-playlist', $event)"
        @download="$emit('download', $event)"
        @download-audio="$emit('download-audio', $event)"
        @play="$emit('play', $event)"
        @play-with-opts="$emit('play-with-opts', $event)"
        @view="$emit('view', $event)"
      />
    </div>
  </div>
</template>

<script>
import Channel from "./Channel";
import NoItems from "@/components/elements/NoItems";
import Loading from "@/components/Loading";
import Utils from "@/Utils";

export default {
  mixins: [Utils],
  emits: [
    'add-to-playlist',
    'download',
    'download-audio',
    'play',
    'play-with-opts',
    'select',
    'view',
  ],

  components: {
    Channel,
    Loading,
    NoItems,
  },

  props: {
    selectedChannel: {
      type: Object,
      default: null,
    },

    filter: {
      type: String,
      default: null,
    },
  },

  data() {
    return {
      channels: [],
      loading: false,
      nextPageToken: null,
    }
  },

  computed: {
    channelsById() {
      return this.channels
        .filter(channel => !this.filter || channel.name.toLowerCase().includes(this.filter.toLowerCase()))
        .reduce((acc, channel) => {
          acc[channel.id] = channel
          return acc
        }, {})
    },

    showLoading() {
      return this.loading && !this.channels.length
    },
  },

  methods: {
    async loadSubscriptions() {
      if (this.loading)
        return

      this.loading = true

      try {
        this.channels = [
          ...this.channels,
          ...(await this.request('youtube.get_subscriptions', {page: this.nextPageToken}))
        ]
        if (this.channels.length) {
          this.nextPageToken = this.channels[this.channels.length - 1].next_page_token
        }
      } finally {
        this.loading = false
      }
    },

    initView() {
      const args = this.getUrlArgs()
      if (args.channel) {
        this.$emit('select', {id: args.channel})
      }
    },

    onScroll(e) {
      const el = e.target
      if (!el)
        return

      const bottom = (el.scrollHeight - el.scrollTop) <= el.clientHeight + 150
      if (!bottom)
        return

      this.loadSubscriptions()
    },
  },

  async mounted() {
    await this.loadSubscriptions()
    this.initView()
  },
}
</script>

<style lang="scss" scoped>
.media-youtube-subscriptions {
  height: 100%;

  .subscriptions-index {
    height: 100%;
    overflow-y: auto;
  }

  .channel.item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: $default-border-2;
    box-shadow: $border-shadow-bottom;
    border-radius: 0.5em;
    cursor: pointer;

    .image {
      width: 100%;
      height: 10em;
      display: flex;
      align-items: center;
      justify-content: center;

      img {
        width: 5em;
        height: 5em;
        border-radius: 0.5em;
        transition: filter 0.2s ease-in-out;
      }
    }

    .title {
      font-size: 1.1em;
      margin-top: 0.5em;
    }

    &:hover {
      text-decoration: underline;

      img {
        filter: contrast(70%);
      }
    }
  }

  .subscription-body {
    height: 100%;
  }
}
</style>

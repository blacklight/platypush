<template>
  <div class="media-youtube-subscriptions">
    <div class="subscriptions-index" v-if="!selectedChannel">
      <Loading v-if="loading" />
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
      <Channel :id="selectedChannel" :filter="filter" @play="$emit('play', $event)" />
    </div>
  </div>
</template>

<script>
import Channel from "./Channel";
import NoItems from "@/components/elements/NoItems";
import Loading from "@/components/Loading";
import Utils from "@/Utils";

export default {
  emits: ['play', 'select'],
  mixins: [Utils],
  components: {
    Channel,
    Loading,
    NoItems,
  },

  props: {
    selectedChannel: {
      type: String,
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
  },

  methods: {
    async loadSubscriptions() {
      this.loading = true
      try {
        this.channels = (await this.request('youtube.get_subscriptions'))
      } finally {
        this.loading = false
      }
    },
  },

  mounted() {
    this.loadSubscriptions()
  },
}
</script>

<style lang="scss" scoped>
.media-youtube-subscriptions {
  height: 100%;

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

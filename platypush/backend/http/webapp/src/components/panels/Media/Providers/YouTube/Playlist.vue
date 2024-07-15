<template>
  <div class="media-youtube-playlist">
    <Loading v-if="loading" />

    <div class="playlist-container" v-else>
      <div class="header">
        <div class="banner">
          <img :src="metadata?.image" v-if="metadata?.image?.length" />
        </div>

        <div class="row info-container">
          <div class="info">
            <div class="row">
              <a class="title" :href="metadata?.url" target="_blank" rel="noopener noreferrer" v-if="metadata?.url">
                {{ name }}
              </a>

              <span class="title" v-else>
                {{ name }}
              </span>

              <div class="n-items">{{ nItems }} videos</div>
            </div>

            <div class="row" v-if="metadata?.description">
              <div class="description">
                {{ metadata?.description }}
              </div>
            </div>

            <div class="row" v-if="metadata?.channel_url">
              <div class="channel">
                Uploaded by
                <a :href="metadata.channel_url" target="_blank" rel="noopener noreferrer">
                  {{ metadata?.channel }}
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <NoItems :with-shadow="false" v-if="!nItems">
        No videos found.
      </NoItems>

      <Results :results="items"
               :sources="{'youtube': true}"
               :filter="filter"
               :playlist="id"
               :selected-result="selectedResult"
               @add-to-playlist="$emit('add-to-playlist', $event)"
               @download="$emit('download', $event)"
               @play="$emit('play', $event)"
               @remove-from-playlist="$emit('remove-from-playlist', $event)"
               @select="selectedResult = $event"
               v-else />
    </div>
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
    'play',
    'remove-from-playlist',
  ],

  components: {
    Loading,
    NoItems,
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

    metadata: {
      type: Object,
      default: null,
    },
  },

  data() {
    return {
      items: [],
      loading: false,
      selectedResult: null,
    }
  },

  computed: {
    name() {
      return this.metadata?.title || this.metadata?.name
    },

    nItems() {
      return this.metadata?.videos || this.items?.length || 0
    },
  },

  methods: {
    async loadItems() {
      this.loading = true
      try {
        this.items = (
          await this.request('youtube.get_playlist', {id: this.id})
        ).map(item => ({
          ...item,
          type: 'youtube',
        }))
      } finally {
        this.loading = false
      }
    },
  },

  mounted() {
    this.loadItems()
  },
}
</script>

<style lang="scss" scoped>
@import "header.scss";

.media-youtube-playlist {
  height: 100%;

  .playlist-container {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .header {
    .banner {
      opacity: 0.75;
    }

    .channel {
      flex: 1;
    }
  }
}
</style>

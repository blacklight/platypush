<template>
  <div class="embed-player">
    <div class="player-container" :class="{ youtube: !!youtubeUrl }">
      <Loading v-if="loading" />

      <iframe :src="youtubeUrl"
              class="player"
              allowfullscreen
              frameborder="0"
              v-else-if="youtubeUrl" />

      <div class="audio-container" v-else-if="isAudio">
        <div class="poster-container" v-if="poster">
          <img :src="poster" />
        </div>
        <audio ref="audio"
               class="player"
               controls
               @canplay="$refs.audio.play()"
               @ended="$emit('ended')">
          <source :src="mediaItem.url" :type="mediaItem.mime_type">
        </audio>
      </div>

      <video ref="video"
             class="player"
             controls
             :poster="poster"
             @canplay="$refs.video.play()"
             @ended="$emit('ended')"
             v-else-if="mediaItem">
        <source :src="mediaItem.url" :type="mediaItem.mime_type">
      </video>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import Loading from "@/components/Loading";
import MediaUtils from "@/components/Media/Utils";

export default {
  components: {
    Loading,
  },
  emits: ['ended'],
  mixins: [MediaUtils],
  props: {
    item: {
      type: Object,
      required: true,
    },

    pluginName: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      loading: false,
      mediaItem: null,
    }
  },

  computed: {
    isAudio() {
      return (this.mediaItem?.mime_type || '').startsWith('audio')
    },

    poster() {
      if (this.isAudio && this.item?.image) {
        return this.item.image
      }

      return null
    },

    youtubeUrl() {
      if (this.item.type !== 'youtube')
        return null

      const youtubeId = this.item.url.match(/(?:\?v=|\/embed\/|\/\d\/|\/vi\/|\/v\/|https?:\/\/(?:www\.)?youtu\.be\/)([^?&"'>]+)/)[1]
      return `https://www.youtube-nocookie.com/embed/${youtubeId}?autoplay=1`
    },
  },

  methods: {
    async refresh() {
      this.loading = true

      try {
        if (this.item.type === 'file') {
          let streamable = null
          let error = false
          this.loading = true

          try {
            streamable = await this.startStreaming(this.item.url, this.pluginName)
          } catch (e) {
            error = true
          } finally {
            this.opening = false
            if (!streamable) {
              this.notify({
                title: 'Error starting streaming',
                text: error || 'Unknown error',
                error: true,
              })
            }
          }

          if (!streamable)
            return

          this.mediaItem = {
            ...this.item,
            url: streamable.url,
            mime_type: streamable.mime_type,
          }
        } else if (this.item.type !== 'youtube') {
          const response = await axios.head(this.item.url)
          this.mediaItem = {
            ...this.item,
            mime_type: response.headers["content-type"],
          }
        }
      } finally {
        this.loading = false
      }
    },
  },

  watch: {
    item: {
      handler() {
        this.refresh()
      },
      deep: true,
    },
  },

  mounted() {
    this.refresh()
  },
}
</script>

<style lang="scss" scoped>
@import "~@/components/Media/vars";

$audio-height: 2.5em;

.embed-player {
  position: relative;
  width: 100%;
  height: 100%;
  background-color: black;
  overflow: hidden;

  .player-container {
    position: relative;
    width: 100%;
    height: 100%;

    &.youtube {
      min-width: 95vw;
      min-height: 90vh;
    }
  }

  .audio-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
    min-width: 50vw;
    min-height: 50vh;
    background-color: black;

    audio {
      height: $audio-height;
    }

    .poster-container {
      width: 100%;
      height: calc(100% - #{$audio-height});
      display: flex;
      justify-content: center;
      align-items: center;

      img {
        max-width: 100%;
        max-height: 100%;
      }
    }
  }

  video, audio {
    width: 100%;
    height: 100%;
  }

  iframe {
    width: 95%;
    height: 95%;
  }
}
</style>

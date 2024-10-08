<template>
  <div class="media-results">
    <Loading v-if="loading" />
    <div class="grid" ref="grid" v-if="results?.length" @scroll="onScroll">
      <Item v-for="(item, i) in visibleResults"
            :key="i"
            :hidden="!!Object.keys(sources || {}).length && !sources[item.type]"
            :item="item"
            :playlist="playlist"
            :selected="selectedResult === i"
            @add-to-playlist="$emit('add-to-playlist', item)"
            @open-channel="$emit('open-channel', item)"
            @remove-from-playlist="$emit('remove-from-playlist', item)"
            @select="$emit('select', i)"
            @play="$emit('play', item)"
            @play-with-opts="$emit('play-with-opts', $event)"
            @view="$emit('view', item)"
            @download="$emit('download', item)"
            @download-audio="$emit('download-audio', item)"
      />
    </div>

    <Modal ref="infoModal" title="Media info" @close="$emit('select', null)">
      <Info :item="results[selectedResult]"
            :pluginName="pluginName"
            @add-to-playlist="$emit('add-to-playlist', results[selectedResult])"
            @download="$emit('download', results[selectedResult])"
            @download-audio="$emit('download-audio', results[selectedResult])"
            @open-channel="$emit('open-channel', results[selectedResult])"
            @play="$emit('play', results[selectedResult])"
            @play-with-opts="$emit('play-with-opts', {...$event, item: results[selectedResult]})"
            v-if="selectedResult != null" />
    </Modal>
  </div>
</template>

<script>
import Info from "@/components/panels/Media/Info";
import Item from "./Item";
import Loading from "@/components/Loading";
import Modal from "@/components/Modal";

export default {
  components: {Info, Item, Loading, Modal},
  emits: [
    'add-to-playlist',
    'download',
    'download-audio',
    'open-channel',
    'play',
    'play-with-opts',
    'remove-from-playlist',
    'scroll-end',
    'select',
    'view',
  ],

  props: {
    loading: {
      type: Boolean,
      default: false,
    },

    pluginName: {
      type: String,
    },

    results: {
      type: Array,
      default: () => [],
    },

    selectedResult: {
      type: Number,
    },

    sources: {
      type: Object,
      default: () => {},
    },

    filter: {
      type: String,
      default: null,
    },

    resultIndexStep: {
      type: Number,
      default: 25,
    },

    playlist: {
      default: null,
    },
  },

  data() {
    return {
      maxResultIndex: this.resultIndexStep,
    }
  },

  computed: {
    visibleResults() {
      let results = this.results
        .filter((item) => {
          if (!this.filter?.length)
            return true

          return item.title.toLowerCase().includes(this.filter.toLowerCase())
        })

      if (this.maxResultIndex != null)
        results = results.slice(0, this.maxResultIndex)

      return results
    },
  },

  methods: {
    onScroll(e) {
      const el = e.target
      if (!el)
        return

      const bottom = (el.scrollHeight - el.scrollTop) <= el.clientHeight + 150
      if (!bottom)
        return

      this.$emit('scroll-end')

      if (this.resultIndexStep != null)
        this.maxResultIndex += this.resultIndexStep
    },
  },

  mounted() {
    this.$watch('selectedResult', (value) => {
      if (value?.item_type === 'playlist' || value?.item_type === 'channel') {
        this.$emit('select', null)
        return
      }

      if (value == null)
        this.$refs.infoModal?.close()
      else
        this.$refs.infoModal?.show()
    })
  },
}
</script>

<style lang="scss" scoped>
@import "~@/style/items";
@import "~@/components/Media/vars";

.media-results {
  width: 100%;
  height: 100%;
  background: $background-color;
  position: relative;

  .grid {
    height: 100%;
    overflow: auto;
  }

  .info-container {
    width: 100%;
    cursor: initial;
  }
}
</style>

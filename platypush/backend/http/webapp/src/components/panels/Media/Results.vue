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
            @remove-from-playlist="$emit('remove-from-playlist', item)"
            @select="$emit('select', i)"
            @play="$emit('play', item)"
            @view="$emit('view', item)"
            @download="$emit('download', item)" />
    </div>

    <Modal ref="infoModal" title="Media info" @close="$emit('select', null)">
      <Info :item="results[selectedResult]"
            :pluginName="pluginName"
            @play="$emit('play', results[selectedResult])"
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
    'play',
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
      return this.results
        .filter((item) => {
          if (!this.filter)
            return true

          return item.title.toLowerCase().includes(this.filter.toLowerCase())
        })
        .slice(0, this.maxResultIndex)
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
      this.maxResultIndex += this.resultIndexStep
    },
  },

  mounted() {
    this.$watch('selectedResult', (value) => {
      if (value?.item_type === 'playlist') {
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

<template>
  <div class="media-results" @scroll="onScroll">
    <Loading v-if="loading" />
    <div class="grid" ref="grid" v-if="results?.length">
      <Item v-for="(item, i) in visibleResults"
            :key="i"
            :item="item"
            :selected="selectedResult === i"
            :hidden="!!Object.keys(sources || {}).length && !sources[item.type]"
            @select="$emit('select', i)"
            @play="$emit('play', item)"
            @view="$emit('view', item)"
            @download="$emit('download', item)" />
    </div>

    <Modal ref="infoModal" title="Media info" @close="$emit('select', null)">
      <Info :item="results[selectedResult]"
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
  emits: ['select', 'play', 'view', 'download', 'scroll-end'],
  props: {
    loading: {
      type: Boolean,
      default: false,
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
      if (value == null)
        this.$refs.infoModal?.close()
      else
        this.$refs.infoModal?.show()
    })
  },
}
</script>

<style lang="scss" scoped>
@import "src/style/items";
@import "vars";

.media-results {
  width: 100%;
  height: 100%;
  background: $background-color;
  overflow: auto;

  .info-container {
    width: 100%;
    cursor: initial;
  }
}
</style>

<template>
  <div class="media-results">
    <Loading v-if="loading" />
    <NoItems v-else-if="!results?.length" :with-shadow="false">
      No search results
    </NoItems>

    <div class="grid" v-else>
      <Item v-for="(item, i) in results"
            :key="i"
            :item="item"
            :selected="selectedResult === i"
            :hidden="!sources[item.type]"
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
import NoItems from "@/components/elements/NoItems";

export default {
  components: {Info, Item, Loading, Modal, NoItems},
  emits: ['select', 'play', 'view', 'download'],
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

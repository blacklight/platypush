<template>
  <div class="media-results" :class="{'list': listView}">
    <Loading v-if="loading" />
    <div class="grid" ref="grid" v-if="results?.length" @scroll="onScroll">
      <div class="item-container" v-for="(item, i) in visibleResults" :key="i" ref="item">
        <div class="droppable-container"
             :class="{'dragover': dragOverIndex === i}"
             :ref="'droppable-' + i"
             v-if="playlistView && draggedIndex != null && i > draggedIndex" />

        <Item :item="item"
              :index="i"
              :list-view="listView"
              :playlist="playlist"
              :selected="selectedResult === i"
              :show-date="showDate"
              @add-to-playlist="$emit('add-to-playlist', item)"
              @open-channel="$emit('open-channel', item)"
              @remove-from-playlist="$emit('remove-from-playlist', item)"
              @select="$emit('select', i)"
              @play="$emit('play', item)"
              @play-with-opts="$emit('play-with-opts', $event)"
              @view="$emit('view', item)"
              @download="$emit('download', item)"
              @download-audio="$emit('download-audio', item)"
              @vue:mounted="itemsRef[i] = $event.el"
              @vue:unmounted="delete itemsRef[i]"
        />

        <Draggable :element="itemsRef[i]"
                   @drag="draggedIndex = i"
                   v-if="playlistView" />

        <Droppable :element="itemsRef[i]"
                   @dragenter="dragOverIndex = i"
                   @dragleave="dragOverIndex = null"
                   @dragover="dragOverIndex = i"
                   @drop="onMove(i)" />

        <div class="droppable-container"
             :class="{'dragover': dragOverIndex === i}"
             :ref="'droppable-' + i"
             v-if="playlistView && draggedIndex != null && i < draggedIndex" />

        <Droppable :element="$refs['droppable-' + i]?.[0]"
                   @dragenter="dragOverIndex = i"
                   @dragleave="dragOverIndex = null"
                   @dragover="dragOverIndex = i"
                   @drop="onMove(i)"
                   v-if="playlistView && draggedIndex != null && i !== draggedIndex" />

      </div>
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
import Draggable from "@/components/elements/Draggable"
import Droppable from "@/components/elements/Droppable"
import Info from "@/components/panels/Media/Info";
import Item from "./Item";
import Loading from "@/components/Loading";
import Modal from "@/components/Modal";

export default {
  components: {
    Draggable,
    Droppable,
    Info,
    Item,
    Loading,
    Modal,
  },

  emits: [
    'add-to-playlist',
    'download',
    'download-audio',
    'move',
    'open-channel',
    'play',
    'play-with-opts',
    'remove-from-playlist',
    'scroll-end',
    'select',
    'view',
  ],

  props: {
    filter: {
      type: String,
      default: null,
    },

    listView: {
      type: Boolean,
      default: false,
    },

    loading: {
      type: Boolean,
      default: false,
    },

    playlist: {
      default: null,
    },

    pluginName: {
      type: String,
    },

    results: {
      type: Array,
      default: () => [],
    },

    resultIndexStep: {
      type: Number,
      default: 25,
    },

    selectedResult: {
      type: Number,
    },

    showDate: {
      type: Boolean,
      default: true,
    },

    sources: {
      type: Object,
      default: () => {},
    },
  },

  data() {
    return {
      draggedIndex: null,
      dragOverIndex: null,
      itemsRef: {},
      maxResultIndex: this.resultIndexStep,
    }
  },

  computed: {
    playlistView() {
      return this.playlist != null && this.listView
    },

    visibleResults() {
      let results = this.results
        .filter((item) => {
          if (!this.filter?.length)
            return true

          return (item.title || item.name).toLowerCase().includes(this.filter.toLowerCase())
        })

      if (this.maxResultIndex != null)
        results = results.slice(0, this.maxResultIndex)

      return results
    },
  },

  methods: {
    onMove(toPos) {
      if (this.draggedIndex == null)
        return

      const item = this.results[this.draggedIndex]
      this.$emit('move', {
        from: this.draggedIndex,
        to: toPos,
        item: item,
      })

      this.draggedIndex = null
    },

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

  watch: {
    selectedResult(value) {
      if (value?.item_type === 'playlist' || value?.item_type === 'channel') {
        this.$emit('select', null)
        return
      }

      if (this.selectedResult == null)
        this.$refs.infoModal?.close()
      else
        this.$refs.infoModal?.show()
    },
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

  &.list {
    :deep(.grid) {
      height: fit-content;
      max-height: 100%;
      display: flex;
      flex-direction: column;
      padding: 0;
      row-gap: 0;

      .title {
        font-weight: normal;
      }
    }
  }

  .droppable-container {
    background: $selected-fg;
    box-shadow: $scrollbar-track-shadow;

    &.dragover {
      height: 0.5em;
      background: $active-glow-bg-2;
    }
  }
}
</style>

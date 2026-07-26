<template>
  <div class="media-queue fade-in">
    <Loading v-if="loading" />

    <div class="no-content" v-else-if="!filteredQueue?.length">
      {{ queue?.length ? 'No queue items match the filter' : 'The queue is empty' }}
    </div>

    <div class="items" v-else>
      <div class="item-container"
           v-for="(entry, i) in filteredQueue"
           :key="itemKey(entry.item, entry.index)">
        <div class="droppable-container"
             :class="{'dragover': dragOverIndex === entry.index}"
             :ref="(el) => setDroppableRef(entry.index, el)"
             v-if="draggedIndex != null && entry.index > draggedIndex" />

        <div class="queue-item"
             :class="{selected: selectedItem === i}"
             :ref="(el) => setItemRef(entry.index, el)"
             @click="selectedItem = i">
          <div class="col-1 handle">
            <i class="fa fa-bars" />
          </div>

          <div class="col-1 preview">
            <img v-if="imageUrl(entry.item) && !imageErrors[entry.index]"
                 :src="imageUrl(entry.item)"
                 @error="onImageError(entry.index)"
                 alt="" />
            <i v-else class="fa fa-play-circle" />
          </div>

          <div class="col-7 left side" @dblclick="$emit('play', entry.item)">
            <span class="track-number">{{ i + 1 }}</span>
            <span class="title" v-text="itemTitle(entry.item)" />
          </div>

          <div class="col-3 right side">
            <button @click.stop="$emit('play', entry.item)" title="Play">
              <i class="fa fa-play" />
            </button>
            <button @click.stop="remove(entry.index)" title="Remove from queue">
              <i class="fa fa-trash" />
            </button>
          </div>
        </div>

        <Draggable :element="itemsRef[entry.index]"
                   @drag="draggedIndex = entry.index"
                   v-if="itemsRef[entry.index]" />

        <Droppable :element="itemsRef[entry.index]"
                   @dragenter="dragOverIndex = entry.index"
                   @dragleave="dragOverIndex = null"
                   @dragover="dragOverIndex = entry.index"
                   @drop="onMove(entry.index)"
                   v-if="itemsRef[entry.index]" />

        <div class="droppable-container"
             :class="{'dragover': dragOverIndex === entry.index}"
             :ref="(el) => setDroppableRef(entry.index, el)"
             v-if="draggedIndex != null && entry.index < draggedIndex" />

        <Droppable :element="droppableRefs[entry.index]"
                   @dragenter="dragOverIndex = entry.index"
                   @dragleave="dragOverIndex = null"
                   @dragover="dragOverIndex = entry.index"
                   @drop="onMove(entry.index)"
                   v-if="draggedIndex != null && entry.index !== draggedIndex" />
      </div>
    </div>
  </div>
</template>

<script>
import Draggable from "@/components/elements/Draggable";
import Droppable from "@/components/elements/Droppable";
import Loading from "@/components/Loading";
import Utils from "@/Utils";

export default {
  name: "Queue",
  mixins: [Utils],
  components: {
    Draggable,
    Droppable,
    Loading,
  },

  emits: [
    'play',
    'refresh',
  ],

  props: {
    pluginName: {
      type: String,
      required: true,
    },

    queue: {
      type: Array,
      default: () => [],
    },

    filter: {
      type: String,
      default: '',
    },
  },

  computed: {
    filteredQueue() {
      const filter = (this.filter || '').trim().toLowerCase()
      return this.queue
        .map((item, index) => ({item, index}))
        .filter(({item}) => {
          if (!filter?.length) {
            return true
          }

          const text = (this.itemTitle(item) || '').toString().toLowerCase()
          return text.includes(filter)
        })
    },
  },

  data() {
    return {
      draggedIndex: null,
      dragOverIndex: null,
      droppableRefs: {},
      imageErrors: {},
      itemsRef: {},
      loading: false,
      selectedItem: null,
    }
  },

  methods: {
    itemKey(item, i) {
      return (item.url || item.title || item.name || JSON.stringify(item)) + '-' + i
    },

    itemTitle(item) {
      return item.title || item.name || item.url || item
    },

    imageUrl(item) {
      return item.image || item.thumbnail || item.thumb
    },

    onImageError(i) {
      this.imageErrors[i] = true
    },

    setItemRef(i, el) {
      this.itemsRef[i] = el
    },

    setDroppableRef(i, el) {
      this.droppableRefs[i] = el
    },

    resetDrag() {
      this.draggedIndex = null
      this.dragOverIndex = null
    },

    async onMove(toPos) {
      if (this.draggedIndex == null)
        return

      if (this.draggedIndex === toPos) {
        this.resetDrag()
        return
      }

      try {
        await this.request(
          `${this.pluginName}.move_queue_item`,
          {from_index: this.draggedIndex, to_index: toPos}
        )
      } finally {
        this.resetDrag()
        this.$emit('refresh')
      }
    },

    async remove(index) {
      this.loading = true
      try {
        await this.request(
          `${this.pluginName}.remove_queue_item`,
          {index: index}
        )
      } finally {
        this.loading = false
        this.$emit('refresh')
      }
    },
  },

  watch: {
    queue() {
      this.itemsRef = {}
      this.droppableRefs = {}
      this.imageErrors = {}
    },
  },
}
</script>

<style lang="scss" scoped>
@import "~@/components/Media/vars";
@import "~@/style/items";

.media-queue {
  height: 100%;
  background: $background-color;
  overflow: auto;

  .no-content {
    height: 100%;
  }

  .items {
    display: flex;
    flex-direction: column;
    padding: 0 .5em;
  }

  .item-container {
    width: 100%;
  }

  .queue-item {
    width: 100%;
    display: flex;
    align-items: center;
    padding: .5em;
    border-bottom: 1px solid $default-shadow-color;
    cursor: pointer;

    &.selected {
      background: $selected-bg;
    }

    &:hover {
      background: $hover-bg;
    }

    .handle {
      cursor: grab;
      color: $default-fg-2;
    }

    .preview {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      height: 2em;
      width: 2em;
      min-width: 2em;
      margin-right: .5em;
      border-radius: .2em;
      overflow: hidden;
      background: $default-media-img-bg;
      color: $default-media-img-fg;

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      i {
        font-size: 1.2em;
      }
    }

    .side {
      display: inline-flex;
      align-items: center;
      overflow: hidden;

      &.left {
        .track-number {
          width: 2em;
          color: $default-fg-2;
          margin-right: .5em;
          text-align: right;
          padding: 0 1.75em;
          font-size: 0.9em;
          opacity: 0.75;
        }

        .title {
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }

      &.right {
        justify-content: flex-end;
        flex: 1;

        button {
          background: none;
          border: 0;
          padding: .5em;
          color: $default-fg;

          &:hover {
            color: $default-hover-fg-2;
          }
        }
      }
    }

    .col-1.preview, .col-7.left.side {
      margin: 0;
    }
  }

  .droppable-container {
    background: transparent;

    &.dragover {
      height: .5em;
      background: $active-glow-bg-2;
    }
  }
}
</style>

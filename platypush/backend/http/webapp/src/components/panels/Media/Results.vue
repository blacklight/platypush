<template>
  <div class="media-results">
    <div class="no-content" v-if="!results?.length">
      No search results
    </div>

    <div class="row item" :class="{selected: selectedResult === i, hidden: !sources[result.type]}"
         v-for="(result, i) in results" :key="i" @click="$emit('select', i)">
      <div class="col-10 left side">
        <div class="icon">
          <i :class="typeIcons[result.type]" />
        </div>
        <div class="title" v-text="result.title" />
      </div>

      <div class="col-2 right side">
        <Dropdown title="Actions" icon-class="fa fa-ellipsis-h" @click="$emit('select', i)">
          <DropdownItem icon-class="fa fa-play" text="Play" @click="$emit('play', result)"
                        v-if="result?.type !== 'torrent'" />
          <DropdownItem icon-class="fa fa-download" text="Download" @click="$emit('download', result)"
                        v-if="result?.type === 'torrent'" />
          <DropdownItem icon-class="fa fa-window-maximize" text="View in browser" @click="$emit('view', result)"
                        v-if="result?.type === 'file'" />
          <DropdownItem icon-class="fa fa-info" text="Info" @click="$emit('info', result)" />
        </Dropdown>
      </div>
    </div>
  </div>
</template>

<script>
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";

export default {
  name: "Results",
  components: {Dropdown, DropdownItem},
  emits: ['select', 'info', 'play', 'view', 'download'],
  props: {
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

  data() {
    return {
      typeIcons: {
        'file': 'fa fa-hdd',
        'torrent': 'fa fa-magnet',
        'youtube': 'fab fa-youtube',
        'plex': 'fa fa-plex',
        'jellyfin': 'fa fa-jellyfin',
      },
    }
  },
}
</script>

<style lang="scss" scoped>
@import "src/style/items";

.media-results {
  width: 100%;
  height: 100%;
  background: $background-color;
  overflow: auto;

  .item {
    display: flex;
    align-items: center;

    &.selected {
      background: $selected-bg;
    }

    .side {
      display: inline-flex;
      align-items: center;

      &.right {
        justify-content: flex-end;
        margin-right: .5em;
      }

      :deep(.dropdown-container) {
        .item {
          box-shadow: none;
        }

        button {
          border: 0;
          padding: 0;
          background: none;
          opacity: .7;

          &:hover {
            color: $default-hover-fg-2;
          }
        }
      }
    }
  }

  .no-content {
    height: 100%;
  }

  .icon {
    .fa-youtube {
      color: #d21;
    }
  }
}
</style>

<template>
  <div
    class="item media-item"
    :class="{selected: selected, 'list': listView}"
    @click.right="onContextClick"
    v-if="!hidden">

    <div class="thumbnail" v-if="!listView">
      <MediaImage :item="item" @play="$emit('play')" @select="onMediaSelect" />
    </div>

    <div class="body">
      <div class="row title">
        <div class="left side"
             :class="{'col-11': !listView, 'col-10': listView }"
             @click.stop="$emit('select')">
          <span class="track-number" v-if="listView && item.track_number">
            {{ item.track_number }}
          </span>

          {{item.title || item.name}}
        </div>

        <div class="right side" :class="{'col-1': !listView, 'col-2': listView }">
          <span class="duration" v-if="item.duration && listView">
            <span v-text="formatDuration(item.duration, true)" />
          </span>

          <span class="actions">
            <Dropdown title="Actions" icon-class="fa fa-ellipsis-h" ref="dropdown">
              <DropdownItem v-for="action in actions" :key="action.text"
                            :icon-class="action.iconClass"
                            :text="action.text"
                            @input="action.action" />
            </Dropdown>
          </span>
        </div>
      </div>

      <div class="row subtitle" v-if="item.channel">
        <a class="channel" href="#" target="_blank" @click.prevent="$emit('open-channel')">
          <img :src="item.channel_image" class="channel-image" v-if="item.channel_image" />
          <span class="channel-name" v-text="item.channel" />
        </a>
      </div>

      <div class="row creation-date" v-if="item.created_at && showDate">
        {{ formatDateTime(item.created_at, true) }}
      </div>

      <div class="row creation-date" v-text="item.year" v-else-if="item.year && showDate" />

      <div class="row ratings" v-if="item.critic_rating != null || item.community_rating != null">
        <span class="rating" title="Critic rating" v-if="item.critic_rating != null">
          <i class="fa fa-star" />&nbsp;
          <span v-text="Math.round(item.critic_rating)" />%
        </span>

        <span class="rating" title="Community rating" v-if="item.community_rating != null">
          <i class="fa fa-users" />&nbsp;
          <span v-text="Math.round(item.community_rating)" />%
        </span>
      </div>
    </div>

    <div class="photo-container" v-if="item.item_type === 'photo' && showPhoto">
      <Modal :title="item.title || item.name" :visible="true" @close="showPhoto = false">
        <img :src="item.url" ref="image" @load="onImgLoad" />
      </Modal>
    </div>
  </div>
</template>

<script>
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";
import Icons from "./icons.json";
import MediaImage from "./MediaImage";
import Modal from "@/components/Modal";
import Utils from "@/Utils";

export default {
  mixins: [Utils],
  components: {
    Dropdown,
    DropdownItem,
    MediaImage,
    Modal,
  },

  emits: [
    'add-to-playlist',
    'download',
    'download-audio',
    'open-channel',
    'play',
    'play-with-opts',
    'remove-from-playlist',
    'select',
    'view',
  ],

  props: {
    item: {
      type: Object,
      required: true,
    },

    hidden: {
      type: Boolean,
      default: false,
    },

    listView: {
      type: Boolean,
      default: false,
    },

    playlist: {
      type: String,
    },

    selected: {
      type: Boolean,
      default: false,
    },

    showDate: {
      type: Boolean,
      default: true,
    },
  },

  computed: {
    actions() {
      const actions = []

      if (this.item.type !== 'torrent' && this.item.item_type !== 'photo') {
        actions.push({
          iconClass: 'fa fa-play',
          text: 'Play',
          action: () => this.$emit('play'),
        })
      }

      if (this.item.type === 'youtube') {
        actions.push({
          iconClass: 'fa fa-play',
          text: 'Play (With Cache)',
          action: () => this.$emit('play-with-opts', {item: this.item, opts: {cache: true}}),
        })
      }

      if (this.item.item_type === 'photo') {
        actions.push({
          iconClass: 'fa fa-eye',
          text: 'View',
          action: () => this.showPhoto = true,
        })
      }

      if (this.item.type === 'file') {
        actions.push({
          iconClass: 'fa fa-window-maximize',
          text: 'View in Browser',
          action: () => this.$emit('view'),
        })
      }

      if ((['torrent', 'youtube', 'jellyfin'].includes(this.item.type)) &&
          this.item.item_type !== 'channel' &&
          this.item.item_type !== 'playlist') {
        actions.push({
          iconClass: 'fa fa-download',
          text: 'Download',
          action: () => this.$emit('download'),
        })
      }

      if (this.item.type === 'youtube' &&
          this.item.item_type !== 'channel' &&
          this.item.item_type !== 'playlist') {
        actions.push({
          iconClass: 'fa fa-volume-high',
          text: 'Download Audio',
          action: () => this.$emit('download-audio'),
        })
      }

      if (this.item.type === 'youtube') {
        actions.push({
          iconClass: 'fa fa-list',
          text: 'Add to Playlist',
          action: () => this.$emit('add-to-playlist'),
        })
      }

      if (this.item.type === 'youtube' && this.playlist?.length) {
        actions.push({
          iconClass: 'fa fa-trash',
          text: 'Remove from Playlist',
          action: () => this.$emit('remove-from-playlist'),
        })
      }

      actions.push({
        iconClass: 'fa fa-info-circle',
        text: 'Info',
        action: () => this.$emit('select'),
      })

      return actions
    },
  },

  methods: {
    onContextClick(e) {
      if (this.item?.item_type === 'photo') {
        return
      }

      e.preventDefault()
      this.$refs.dropdown.toggle()
    },

    onImgLoad() {
      const width = this.$refs.image.naturalWidth
      const height = this.$refs.image.naturalHeight

      if (width > height) {
        this.$refs.image.classList.add('horizontal')
      } else {
        this.$refs.image.classList.add('vertical')
      }
    },

    onMediaSelect() {
      if (this.item?.item_type === 'photo') {
        this.showPhoto = true
      } else {
        this.$emit('select')
      }
    },
  },

  data() {
    return {
      showPhoto: false,
      typeIcons: Icons,
    }
  },
}
</script>

<style lang="scss" scoped>
@import "~@/components/Media/vars";

.media-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  max-height: 23.5em;
  height: 100%;
  cursor: initial !important;
  margin-bottom: 5px;
  border: 1px solid transparent;
  border-bottom: 1px solid transparent !important;

  &.selected {
    box-shadow: $border-shadow-bottom;
    background: $selected-bg;
  }

  &:hover {
    background: none !important;
    box-shadow: $border-shadow;
    border-radius: 0.5em;
  }

  .thumbnail {
    max-width: 100%;
  }

  .body {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;

    .row {
      width: 100%;
      display: flex;
      flex-direction: row;
      align-items: center;
    }
  }

  .title {
    display: flex;
    align-items: center;
    font-size: 1.1em;
    font-weight: bold;
    padding: .5em 0;
    flex: 1;
    cursor: pointer;
    overflow: hidden;

    &:hover {
      text-decoration: underline;
    }
  }

  .side {
    display: inline-flex;
    align-items: center;

    &.left {
      max-height: 3em;
      display: flex;
      align-items: flex-start;
      flex-direction: column;
      overflow: hidden;
      text-overflow: " [...]";
      margin-right: 0.5em;
    }

    &.right {
      align-items: flex-end;
      margin-right: 0.5em;
    }

    :deep(.dropdown-container) {
      .item {
        flex-direction: row;
        box-shadow: none;
        cursor: pointer !important;

        &:hover {
          background: $hover-bg !important;
        }
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

  .subtitle {
    font-size: .9em;
    color: $default-fg-2;
    display: flex;
    align-items: center;
    margin-top: .5em;
    flex: 1;

    .channel {
      display: flex;
      align-items: center;

      .channel-name {
        display: inline-flex;
      }
    }
  }

  .channel-image {
    width: 2em;
    height: 2em;
    border-radius: 50%;
    margin-right: .5em;
  }

  .creation-date {
    font-size: .85em;
    color: $default-fg-2;
    flex: 1;
  }

  .ratings {
    width: 100%;
    font-size: .75em;
    opacity: .75;
    display: flex;
    justify-content: space-between;

    .rating {
      display: flex;
      align-items: center;
      margin-right: 1em;

      i {
        margin-right: .25em;
      }
    }
  }

  &.list {
    max-height: none;
    border-bottom: 1px solid $default-shadow-color !important;
    margin: 0;
    padding: 0.25em 0.5em;

    &:hover {
      text-decoration: none;
    }

    .side {
      display: flex;
      align-items: center;

      &.left {
        max-height: none;
        flex-direction: row;
        overflow: visible;
      }

      &.right {
        display: flex;
        justify-content: flex-end;
        margin-right: 0;
      }

      .duration {
        font-size: .9em;
        opacity: .75;
        margin-right: 1em;
      }

      .track-number {
        display: inline-flex;
        font-size: .9em;
        margin-right: 1em;
        color: $default-fg-2;
        justify-content: flex-end;
      }
    }
  }

  .photo-container {
    :deep(.modal) {
      .body {
        max-width: 95vh;
        max-height: 90vh;
        padding: 0;
      }

      img {
        &.horizontal {
          width: 100%;
          height: auto;
          max-width: 95vh;
          max-height: 100%;
        }

        &.vertical {
          width: auto;
          height: 100%;
          max-width: 100%;
          max-height: 90vh;
        }
      }
    }
  }
}
</style>

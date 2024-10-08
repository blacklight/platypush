<template>
  <div
    class="item media-item"
    :class="{selected: selected}"
    @click.right.prevent="$refs.dropdown.toggle()"
    v-if="!hidden">
    <div class="thumbnail">
      <MediaImage :item="item" @play="$emit('play')" @select="$emit('select')" />
    </div>

    <div class="body">
      <div class="row title">
        <div class="col-11 left side" v-text="item.title || item.name" @click="$emit('select')" />
        <div class="col-1 right side">
          <Dropdown title="Actions" icon-class="fa fa-ellipsis-h" ref="dropdown">
            <DropdownItem icon-class="fa fa-play" text="Play" @input="$emit('play')"
                          v-if="item.type !== 'torrent'" />
            <DropdownItem icon-class="fa fa-play" text="Play (With Cache)"
                          @input="$emit('play-with-opts', {item: item, opts: {cache: true}})"
                          v-if="item.type === 'youtube'" />
            <DropdownItem icon-class="fa fa-download" text="Download" @input="$emit('download')"
                          v-if="(item.type === 'torrent' || item.type === 'youtube') && item.item_type !== 'channel' && item.item_type !== 'playlist'" />
            <DropdownItem icon-class="fa fa-volume-high" text="Download Audio" @input="$emit('download-audio')"
                          v-if="item.type === 'youtube' && item.item_type !== 'channel' && item.item_type !== 'playlist'" />
            <DropdownItem icon-class="fa fa-list" text="Add to playlist" @input="$emit('add-to-playlist')"
                          v-if="item.type === 'youtube'" />
            <DropdownItem icon-class="fa fa-trash" text="Remove from playlist" @input="$emit('remove-from-playlist')"
                          v-if="item.type === 'youtube' && playlist?.length" />
            <DropdownItem icon-class="fa fa-window-maximize" text="View in browser" @input="$emit('view')"
                          v-if="item.type === 'file'" />
            <DropdownItem icon-class="fa fa-info-circle" text="Info" @input="$emit('select')" />
          </Dropdown>
        </div>
      </div>

      <div class="row subtitle" v-if="item.channel">
        <a class="channel" href="#" target="_blank" @click.prevent="$emit('open-channel')">
          <img :src="item.channel_image" class="channel-image" v-if="item.channel_image" />
          <span class="channel-name" v-text="item.channel" />
        </a>
      </div>

      <div class="row creation-date" v-if="item.created_at">
        {{ formatDateTime(item.created_at, true) }}
      </div>

      <div class="row creation-date" v-text="item.year" v-else-if="item.year" />

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
  </div>
</template>

<script>
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";
import Icons from "./icons.json";
import MediaImage from "./MediaImage";
import Utils from "@/Utils";

export default {
  components: {Dropdown, DropdownItem, MediaImage},
  mixins: [Utils],
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

    selected: {
      type: Boolean,
      default: false,
    },

    playlist: {
      type: String,
    },
  },

  data() {
    return {
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
}
</style>

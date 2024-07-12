<template>
  <div class="image-container"
       :class="{ 'with-image': !!item?.image }">
    <div class="play-overlay" @click="$emit('play', item)" v-if="hasPlay">
      <i :class="overlayIconClass" />
    </div>

    <span class="icon type-icon" v-if="typeIcons[item?.type]">
      <a :href="item.url" target="_blank" v-if="item.url">
        <i :class="typeIcons[item.type]" :title="item.type">
          &nbsp;
        </i>
      </a>
    </span>

    <img class="image" :src="item.image" :alt="item.title" v-if="item?.image" />
    <div class="image" v-else>
      <div class="inner">
        <i :class="iconClass" />
      </div>
    </div>

    <span class="icon imdb-link" v-if="item?.imdb_id">
      <a :href="`https://www.imdb.com/title/${item.imdb_id}`" target="_blank">
        <i class="fab fa-imdb" />
      </a>
    </span>

    <span class="bottom-overlay duration" v-if="item?.duration != null"
          v-text="convertTime(item.duration)" />
    <span class="bottom-overlay videos" v-else-if="item?.videos != null">
      {{ item.videos }} items
    </span>
  </div>
</template>

<script>
import Icons from "./icons.json";
import MediaUtils from "@/components/Media/Utils";

export default {
  mixins: [Icons, MediaUtils],
  emits: ['play'],
  props: {
    item: {
      type: Object,
      default: () => {},
    },

    hasPlay: {
      type: Boolean,
      default: true,
    },
  },

  data() {
    return {
      typeIcons: Icons,
    }
  },

  computed: {
    iconClass() {
      switch (this.item?.item_type) {
        case 'channel':
          return 'fas fa-user'
        case 'playlist':
          return 'fas fa-list'
        case 'folder':
          return 'fas fa-folder'
        default:
          return 'fas fa-play'
      }
    },

    overlayIconClass() {
      if (
        this.item?.item_type === 'channel' ||
        this.item?.item_type === 'playlist' ||
        this.item?.item_type === 'folder'
      ) {
        return 'fas fa-folder-open'
      }

      return 'fas fa-play'
    },
  },
}
</script>

<style lang="scss" scoped>
@import "~@/components/Media/vars";

.icon {
  position: absolute;
  width: 30px;
  height: 30px;
  font-size: 30px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 0.25em;
  color: $default-media-img-fg;

  a {
    width: 100%;
    height: 100%;
    color: $default-media-img-fg;

    &:hover {
      color: $default-hover-fg;
    }
  }

  i {
    margin: 2.5px;
  }

  .fa-imdb {
    position: absolute;
    top: 0;
    margin: 1px 2.5px 3px 2.5px;
  }

  .fa-youtube {
    margin-left: 1px;
  }
}

.imdb-link {
  top: 0;
  right: 0;
}

.bottom-overlay {
  position: absolute;
  bottom: 0;
  right: 0;
  font-size: 0.9em;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  padding: 0.25em 0.5em;
  border-radius: 0.25em;
}

.type-icon {
  top: 0;
  left: 0;
  font-size: 25px;
}

.image-container {
  max-width: 100%;
  min-height: 200px;
  aspect-ratio: 16 / 9;
  display: flex;
  justify-content: center;
  position: relative;

  &.with-image {
    background: black;

    .icon {
      background: none;
    }

    .play-overlay {
      border-radius: 0;
    }
  }

  img {
    height: 100%;
  }
}

.image {
  max-width: 100%;
}

div.image {
  width: 100%;
  color: $default-media-img-fg;
  font-size: 5em;
  display: flex;
  align-items: center;
  justify-content: center;

  .inner {
    width: 100%;
    height: 100%;
    background: $default-media-img-bg;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 0.5em;
  }
}

.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 2em;
  opacity: 0;
  transition: opacity 0.2s ease-in-out;

  &:hover {
    opacity: 1;
  }

  i {
    font-size: 5em;
    color: $default-media-img-fg;
  }
}
</style>

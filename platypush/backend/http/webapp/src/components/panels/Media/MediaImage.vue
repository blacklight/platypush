<template>
  <div class="image-container">
    <img class="image" :src="item.image" :alt="item.title" v-if="item?.image" />
    <div class="image" v-else>
      <div class="inner">
        <i class="fas fa-play" />
      </div>
    </div>

    <span class="imdb-link" v-if="item?.imdb_id">
      <a :href="`https://www.imdb.com/title/${item.imdb_id}`" target="_blank">
        <i class="fab fa-imdb" />
      </a>
    </span>

    <span class="duration" v-if="item?.duration != null"
          v-text="convertTime(item.duration)" />
  </div>
</template>

<script>
import MediaUtils from "@/components/Media/Utils";

export default {
  mixins: [MediaUtils],
  props: {
    item: {
      type: Object,
      default: () => {},
    }
  }
}
</script>

<style lang="scss" scoped>
@import "vars";

.imdb-link {
  position: absolute;
  top: 0;
  right: 0;
  height: 1em;
  font-size: 2em;

  &:hover {
    color: $default-hover-fg;
  }

  i {
    background: #ffff00;
    border-radius: 0.25em;
  }
}

.duration {
  position: absolute;
  bottom: 0;
  right: 0;
  font-size: 0.9em;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  padding: 0.25em 0.5em;
  border-radius: 0.25em;
}

.image-container {
  width: 100%;
  min-height: 240px;
  position: relative;

  img {
    @include from($tablet) {
      height: 480px;
    }
  }
}

div.image {
  height: 400px;
  color: $default-media-img-fg;
  font-size: 5em;
  display: flex;
  align-items: center;
  justify-content: center;

  .inner {
    width: calc(100% - 20px);
    height: calc(100% - 20px);
    min-height: 240px;
    background: $default-media-img-bg;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 1em;
  }
}
</style>

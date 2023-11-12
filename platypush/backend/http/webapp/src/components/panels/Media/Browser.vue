<template>
  <keep-alive>
    <div class="media-browser">
      <Loading v-if="loading" />

      <div class="media-index grid" v-else-if="!collection">
        <div class="item" @click="collection = 'files'">
          <div class="icon">
            <i class="fas fa-folder"></i>
          </div>
          <div class="name">
            Files
          </div>
        </div>
      </div>

      <div class="media-browser fade-in" v-else>
        <Browser :is-media="true"
           :filter="filter"
           :has-back="true"
           @back="collection = null"
           @path-change="$emit('path-change', $event)"
           @play="$emit('play', $event)"
           v-if="collection === 'files'" />
      </div>
    </div>
  </keep-alive>
</template>

<script>
import Browser from "@/components/File/Browser";
import Loading from "@/components/Loading";

export default {
  emits: ['path-change', 'play'],
  components: {
    Browser,
    Loading,
  },

  props: {
    filter: {
      type: String,
      default: '',
    },
  },

  data() {
    return {
      loading: false,
      collection: null,
    }
  },
}
</script>

<style lang="scss" scoped>
.media-browser {
  height: 100%;

  .item {
    height: 100px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: $default-border-2;
    cursor: pointer;

    &:hover {
      background: $hover-bg;
    }

    .icon {
      height: 60%;
      display: inline-flex;
      justify-content: center;
      opacity: 0.5;

      i {
        font-size: 40px;
      }
    }
  }
}
</style>

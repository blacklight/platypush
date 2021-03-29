<template>
  <div class="camera component-row">
    <div class="feed-container" ref="container">
      <div class="no-content" v-text="name" v-if="!visible" />
      <img alt="Camera feed" :src="imgUrl" v-if="visible && type === 'image'">
      <video v-else-if="visible && type === 'video'">
        <source :src="src">
      </video>
    </div>

    <div class="controls">
      <button class="toggle-btn" @click="visible = !visible">
        <i class="fa fa-play" v-if="!visible" />
        <i class="fa fa-pause" v-else />
      </button>
    </div>
  </div>
</template>

<script>
import Utils from "@/Utils";

/**
 * This component can be used to view a feed from a camera.
 */
export default {
  name: "Camera",
  mixins: [Utils],
  props: {
    /**
     * Camera feed URL.
     * For instance, in the case of a PiCamera feed: http://host:8008/camera/pi/video.mjpeg
     */
    src: {
      type: String,
      required: true,
    },

    /**
     * Camera feed type - it can be "image" (usually in case of MJPEG feeds) or "video".
     */
    type: {
      type: String,
      default: "image",
    },

    /**
     * Camera feed name.
     */
    name: {
      type: String,
    },
  },

  computed: {
    imgUrl() {
      if (this.type !== 'image')
        return

      return this.src + (this.src.indexOf('?') > 0 ? '&' : '?') + '_t=' + (new Date().getTime().toString())
    },
  },

  data() {
    return {
      visible: false,
    }
  },
}
</script>

<style lang="scss" scoped>
.camera {
  width: calc(100% + 2em);
  height: calc(100% + 2em);
  position: relative;
  background: black;
  color: #888;
  margin: -1em;

  .feed-container {
    width: 100%;
    height: calc(100% - 3em);
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .controls {
    width: 100%;
    height: 3em;
    position: absolute;
    bottom: 0;

    button {
      background: none;
      border: none;
      color: #888;
    }
  }
}
</style>

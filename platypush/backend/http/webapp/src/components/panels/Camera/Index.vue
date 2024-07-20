<template>
  <div class="camera" ref="cameraRoot">
    <div class="camera-container"
         :class="{fullscreen: fullscreen_}"
         ref="cameraContainer">
      <div class="frame-canvas" ref="frameCanvas">
        <div class="frame-container"
             :class="{vertical: isCameraVertical, horizontal: !isCameraVertical}"
             :style="{aspectRatio: aspectRatio}"
             ref="frameContainer">
          <div class="no-frame" v-if="!streaming && !capturing && !captured">The camera is not active</div>
          <img class="frame" :src="url" ref="frame" alt="">
        </div>
      </div>

      <div class="controls">
        <div class="left">
          <button type="button" @click="startStreaming" :disabled="capturing" title="Start video" v-if="!streaming">
            <i class="fa fa-play" />
          </button>

          <button type="button" @click="stopStreaming" :disabled="capturing" title="Stop video" v-else>
            <i class="fa fa-stop" />
          </button>

          <button type="button" @click="capture" :disabled="streaming || capturing" v-if="!streaming"
                  title="Take a picture">
            <i class="fas fa-camera" />
          </button>
        </div>

        <div class="right">
          <button type="button" @click="startAudio" title="Start audio" v-if="!audioOn">
            <i class="fas fa-volume-mute" />
          </button>

          <button type="button" @click="stopAudio" title="Stop audio" v-else>
            <i class="fas fa-volume-up" />
          </button>

          <button type="button" @click="$refs.paramsModal.show()" title="Settings">
            <i class="fas fa-cog" />
          </button>

          <button type="button"
                  :title="fullscreen_ ? 'Exit fullscreen' : 'Fullscreen'"
                  @click="fullscreen_ = !fullscreen_"
                  v-if="!fullscreen">
            <i class="fas fa-expand" v-if="!fullscreen_" />
            <i class="fas fa-compress" v-else />
          </button>
        </div>
      </div>
    </div>

    <div class="audio-container">
      <audio autoplay preload="none" ref="player" v-if="audioOn">
        <source :src="`/sound/stream.aac?t=${(new Date()).getTime()}`">
        Your browser does not support audio elements
      </audio>
    </div>

    <div class="url" v-if="url?.length">
      <label class="row">
        <span class="name">Stream URL</span>
        <input name="url" type="text" :value="fullURL" disabled="disabled"/>
      </label>
    </div>

    <Modal ref="paramsModal" title="Camera Parameters">
      <div class="params">
        <label class="row">
          <span class="name">Device</span>
          <input name="device" type="text" v-model="attrs.device" @change="onDeviceChanged"/>
        </label>

        <label class="row">
          <span class="name">Width</span>
          <input name="width" type="text" v-model="attrs.resolution[0]" @change="onSizeChanged"/>
        </label>

        <label class="row">
          <span class="name">Height</span>
          <input name="height" type="text" v-model="attrs.resolution[1]" @change="onSizeChanged"/>
        </label>

        <label class="row">
          <span class="name">Horizontal Flip</span>
          <input name="horizontal_flip" type="checkbox" v-model="attrs.horizontal_flip" @change="onFlipChanged"/>
        </label>

        <label class="row">
          <span class="name">Vertical Flip</span>
          <input name="vertical_flip" type="checkbox" v-model="attrs.vertical_flip" @change="onFlipChanged"/>
        </label>

        <label class="row">
          <span class="name">Rotate</span>
          <input name="rotate" type="text" v-model="attrs.rotate" @change="onSizeChanged"/>
        </label>

        <label class="row">
          <span class="name">Scale-X</span>
          <input name="scale_x" type="text" v-model="attrs.scale_x" @change="onSizeChanged"/>
        </label>

        <label class="row">
          <span class="name">Scale-Y</span>
          <input name="scale_y" type="text" v-model="attrs.scale_y" @change="onSizeChanged"/>
        </label>

        <label class="row">
          <span class="name">Frames per second</span>
          <input name="fps" type="text" v-model="attrs.fps" @change="onFpsChanged"/>
        </label>

        <label class="row">
          <span class="name">Grayscale</span>
          <input name="grayscale" type="checkbox" v-model="attrs.grayscale" @change="onGrayscaleChanged"/>
        </label>

        <slot />
      </div>
    </Modal>
  </div>
</template>

<script>
import CameraMixin from "@/components/panels/Camera/Mixin";
import Modal from "@/components/Modal";

export default {
  name: "Camera",
  components: {Modal},
  mixins: [CameraMixin],

  computed: {
    fullURL() {
      return `${window.location.protocol}//${window.location.host}${this.url}`
    },
  },

  methods: {
    startStreaming() {
      this._startStreaming(this.cameraPlugin)
    },

    capture() {
      this._capture(this.cameraPlugin)
    },
  },
}
</script>

<style lang="scss">
@import "common";
</style>

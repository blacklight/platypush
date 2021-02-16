<template>
  <div class="camera">
    <div class="camera-container">
      <div class="frame-container" ref="frameContainer">
        <div class="no-frame" v-if="!streaming && !capturing && !captured">The camera is not active</div>
        <img class="frame" :src="url" ref="frame" alt="">
      </div>

      <div class="controls">
        <div class="left">
          <button type="button" @click="startStreaming" :disabled="capturing" title="Start video" v-if="!streaming">
            <i class="fa fa-play" />
          </button>

          <button type="button" @click="stopStreaming" :disabled="capturing" title="Stop video" v-else>
            <i class="fa fa-stop" />
          </button>

          <button type="button" @click="capture" :disabled="streaming || capturing" title="Take a picture">
            <i class="fas fa-camera" />
          </button>
        </div>

        <div class="right">
          <button type="button" @click="$refs.paramsModal.show()" title="Settings">
            <i class="fas fa-cog" />
          </button>
        </div>
      </div>
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

        <Slot />
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
  props: {
    cameraPlugin: {
      type: String,
      required: true,
    },
  },

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
$camera-background: #101520;

.camera {
  width: 100%;
  height: 100%;
  background: $background-color;
  overflow: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 3em;

  .camera-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    background: $camera-background;

    .frame-container {
      position: relative;
    }

    .frame, .no-frame {
      position: absolute;
      top: 0;
      width: 100%;
      height: 100%;
    }

    .frame {
      z-index: 1;
    }

    .no-frame {
      display: flex;
      color: white;
      align-items: center;
      justify-content: center;
      z-index: 2;
      background: black;
    }

    .controls {
      width: 100%;
      display: flex;
      border-top: 1px solid #202530;
      padding: .5em .25em;

      .left,.right {
        width: 50%;
      }

      .right {
        text-align: right;
      }

      button {
        background: none;
        color: white;
        border: none;

        &:hover {
          color: $default-hover-fg-2;
        }
      }
    }
  }

  .url {
    @media screen and (max-width: calc(#{$tablet} - 1px)) {
      width: 80%;
    }

    @media screen and (min-width: $tablet) {
      width: 640px;
    }

    display: flex;
    margin: 1em;

    .row {
      width: 100%;
      display: flex;
      align-items: center;
    }

    .name {
      width: 140px;
    }

    input {
      width: 500px;
      font-weight: normal;
    }
  }

  .params {
    @media screen and (min-width: $tablet) {
      width: 640px;
    }

    display: flex;
    flex-direction: column;
    margin: -2em;

    label {
      font-weight: normal;
    }

    .head {
      display: flex;
      justify-content: center;

      label {
        width: 100%;
        display: flex;
        justify-content: right;

        .name {
          margin-right: 1em;
        }
      }
    }

    .row {
      width: 100%;
      display: flex;
      align-items: center;
      padding: 0.5em 1em;

      .name {
        width: 30%;
      }

      input {
        width: 70%;
      }

      &:nth-child(even) {
        background: $default-bg-4;
      }

      &:hover {
        background: $hover-bg;
      }
    }
  }

  .modal {
    .content {
      @media screen and (max-width: calc(#{$tablet} - 1px)) {
        width: 90% !important;
      }
    }
  }
}
</style>

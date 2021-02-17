<template>
  <div class="camera">
    <Loading v-if="loading" />

    <div class="camera-selector">
      <div class="left">
        <label>
          <select ref="cameraSelector" @change="onCameraSelected">
            <option selected disabled v-if="!Object.keys(cameras).length">-- No cameras available</option>
            <option v-for="name in Object.keys(cameras)" :key="name" :value="name" v-text="name" />
          </select>
        </label>
      </div>

      <div class="right">
        <button type="button" @click="updateCameraStatus" :disabled="loading">
          <i class="fas fa-sync-alt" title="Refresh cameras" />
        </button>
      </div>
    </div>

    <div class="camera-container">
      <div class="frame-container" ref="frameContainer">
        <div class="no-frame" v-if="!streaming && !capturing && !captured">The camera is not active</div>
        <img class="frame" ref="frame" alt="" src="">
      </div>

      <div class="controls">
        <div class="left">
          <button type="button" @click="startStreaming" :disabled="capturing || loading" v-if="!streaming">
            <i class="fa fa-play" title="Start video" />
          </button>

          <button type="button" @click="stopStreaming" :disabled="capturing || loading" v-else>
            <i class="fa fa-stop" title="Stop video" />
          </button>

          <button type="button" @click="capture" :disabled="streaming || capturing || loading">
            <i class="fas fa-camera" title="Take a picture" />
          </button>
        </div>

        <div class="right">
          <button type="button" @click="flipCamera" :disabled="loading">
            <i class="fas fa-retweet" title="Flip camera" />
          </button>

          <button type="button" @click="recording = true" v-if="!recording" :disabled="loading">
            <i class="fa fa-volume-mute" title="Start audio" />
          </button>

          <button type="button" @click="recording = false" v-else :disabled="loading">
            <i class="fa fa-volume-up" title="Stop audio" />
          </button>
        </div>
      </div>
    </div>

    <div class="sound-container">
      <audio autoplay preload="none" ref="player" v-if="recording">
        <source :src="cameras[selectedCamera].audio_url" type="audio/x-wav;codec=pcm">
        Your browser does not support audio elements
      </audio>
    </div>
  </div>
</template>

<script>
import Utils from "@/Utils";
import Loading from "@/components/Loading";

export default {
  name: "CameraAndroidIpcam",
  components: {Loading},
  mixins: [Utils],

  data() {
    return {
      loading: false,
      streaming: false,
      capturing: false,
      recording: false,
      captured: false,
      cameras: {},
      selectedCamera: undefined,
    }
  },

  computed: {
    config() {
      return this.$root.config['camera.android.ipcam']
    },
  },

  methods: {
    startStreaming() {
      if (this.streaming)
        return

      const cam = this.cameras[this.selectedCamera]
      this.streaming = true
      this.capturing = false
      this.captured = false
      this.$refs.frame.setAttribute('src', cam.stream_url)
    },

    stopStreaming() {
      if (!this.streaming)
        return

      this.streaming = false
      this.capturing = false
      this.$refs.frame.removeAttribute('src')
    },

    capture() {
      if (this.capturing)
        return

      const cam = this.cameras[this.selectedCamera]
      this.streaming = false
      this.capturing = true
      this.captured = true
      this.$refs.frame.setAttribute('src', cam.image_url + '?t=' + (new Date()).getTime())
    },

    onFrameLoaded() {
      if (this.capturing)
        this.capturing = false
    },

    onCameraSelected(event) {
      this.selectedCamera = event.target.value
    },

    async flipCamera() {
      const cam = this.cameras[this.selectedCamera]
      this.loading = true

      try {
        const value = !cam.ffc
        await this.request('camera.android.ipcam.set_front_facing_camera', {
          activate: value, camera: cam.name
        })

        this.cameras[this.selectedCamera].ffc = value
      } finally {
        this.loading = false
      }
    },

    async updateCameraStatus() {
      this.loading = true

      try {
        const cameras = await this.request('camera.android.ipcam.status')
        this.cameras = cameras.reduce((cameras, cam) => {
          for (const attr of ['stream_url', 'image_url', 'audio_url']) {
            if (cam[attr].startsWith('https://')) {
              cam[attr] = cam[attr].replace('https://', 'http://')
            }

            if (cam.name in this.config.cameras && this.config.cameras[cam.name].username) {
              cam[attr] = 'http://' + this.config.cameras[cam.name].username + ':' +
                  this.config.cameras[cam.name].password + '@' + cam[attr].substr(7)
            }
          }

          cameras[cam.name] = cam
          return cameras
        }, {})

        if (cameras.length)
          this.selectedCamera = cameras[0].name

      } finally {
        this.loading = false
      }
    },
  },

  mounted() {
    this.$refs.frame.addEventListener('load', this.onFrameLoaded)
    this.updateCameraStatus()
  },
}
</script>

<style lang="scss" scoped>
@import "../Camera/common";

$controls-height: 3.5em;

.camera {
  .camera-selector {
    width: 100%;
    height: $controls-height;
    margin-top: -3em;
    box-shadow: $border-shadow-bottom;
    display: flex;
    align-items: center;

    .left,
    .right {
      display: flex;
    }

    .left {
      width: 90%;
    }

    .right {
      width: 10%;
      justify-content: right;
    }

    label {
      width: 100%;
      padding-left: 1em;
      select {
        width: 100%;
      }
    }

    button {
      background: none;
      border: none;
      &:hover {
        color: $default-hover-fg;
      }
    }
  }

  .camera-container {
    margin-top: 2em;
    min-width: 640px;
    min-height: calc(480px + #{$controls-height});

    .frame-container {
      min-width: 640px;
      min-height: 480px;
    }

    .controls {
      height: $controls-height;
    }
  }
}

//.camera {
//  min-height: 90%;
//  overflow: auto;
//  display: flex;
//  flex-direction: column;
//  align-items: center;
//
//  .camera-container {
//    min-width: 640px;
//    min-height: 480px;
//    position: relative;
//    background: black;
//    margin-bottom: 1em;
//
//    .frame, .no-frame {
//      position: absolute;
//      top: 0;
//      width: 100%;
//      height: 100%;
//    }
//
//    .frame {
//      z-index: 1;
//    }
//
//    .no-frame {
//      display: flex;
//      background: rgba(0, 0, 0, 0.1);
//      color: white;
//      align-items: center;
//      justify-content: center;
//      z-index: 2;
//    }
//  }
//}
</style>

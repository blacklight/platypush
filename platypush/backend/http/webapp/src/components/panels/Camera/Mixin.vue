<script>
import Utils from "@/Utils";

export default {
  name: "CameraMixin",
  mixins: [Utils],

  props: {
    cameraPlugin: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      streaming: false,
      capturing: false,
      captured: false,
      audioOn: false,
      url: null,
      attrs: {},
    }
  },

  computed: {
    params() {
      return {
        resolution: this.attrs.resolution,
        device: this.attrs.device?.length ? this.attrs.device : null,
        horizontal_flip: parseInt(0 + this.attrs.horizontal_flip),
        vertical_flip: parseInt(0 + this.attrs.vertical_flip),
        rotate: parseFloat(this.attrs.rotate),
        scale_x: parseFloat(this.attrs.scale_x),
        scale_y: parseFloat(this.attrs.scale_y),
        fps: parseFloat(this.attrs.fps),
        grayscale: parseInt(0 + this.attrs.grayscale),
      }
    },
  },

  methods: {
    getUrl(plugin, action) {
      return '/camera/' + plugin + '/' + action + '?' +
          Object.entries(this.params).filter((entry) => entry[1] != null && ('' + entry[1]).length > 0)
              .map(([k, v]) => k + '=' + v).join('&')
    },

    _startStreaming(plugin) {
      if (this.streaming)
        return

      this.streaming = true
      this.capturing = false
      this.captured = false
      this.url = this.getUrl(plugin, 'video.' + this.attrs.stream_format)
    },

    stopStreaming() {
      if (!this.streaming)
        return

      this.streaming = false
      this.capturing = false
      this.url = null
    },

    _capture(plugin) {
      if (this.capturing)
        return

      this.streaming = false
      this.capturing = true
      this.captured = true
      this.url = this.getUrl(plugin, 'photo.jpg') + '&t=' + (new Date()).getTime()
    },

    onFrameLoaded() {
      if (this.capturing) {
        this.capturing = false
      }
    },

    onDeviceChanged() {},
    onFlipChanged() {},
    onSizeChanged() {
      const degToRad = (deg) => (deg * Math.PI)/180
      const rot = degToRad(this.params.rotate)
      let width = Math.round(this.params.scale_x * Math.abs(this.params.resolution[0] * Math.cos(rot) + this.params.resolution[1] * Math.sin(rot)))
      let height = Math.round(this.params.scale_y * Math.abs(this.params.resolution[0] * Math.sin(rot) + this.params.resolution[1] * Math.cos(rot)))

      if (width > window.innerWidth) {
        height = Math.round(height * (window.innerWidth / width))
        width = window.innerWidth
      }

      if (height > window.innerHeight) {
        width = Math.round(width * (window.innerHeight / height))
        height = window.innerHeight
      }

      this.$refs.frameContainer.style.width = `${width}px`
      this.$refs.frameContainer.style.height = `${height}px`
    },

    onFpsChanged() {},
    onGrayscaleChanged() {},

    startAudio() {
      this.audioOn = true
    },

    async stopAudio() {
      this.audioOn = false
      await this.request('sound.stop_recording')
    },
  },

  created() {
    const config = this.$root.config[`camera.${this.cameraPlugin}`] || {}
    this.attrs = {
      resolution: config.resolution || [640, 480],
      device: config.device,
      horizontal_flip: config.horizontal_flip || 0,
      vertical_flip: config.vertical_flip || 0,
      rotate: config.rotate || 0,
      scale_x: config.scale_x || 1.0,
      scale_y: config.scale_y || 1.0,
      fps: config.fps || 16.0,
      grayscale: config.grayscale || 0,
      stream_format: config.stream_format || 'mjpeg',
    }
  },

  mounted() {
    this.$refs.frame.addEventListener('load', this.onFrameLoaded)
    this.onSizeChanged()
    this.$watch(() => this.attrs.resolution, this.onSizeChanged)
    this.$watch(() => this.attrs.horizontal_flip, this.onSizeChanged)
    this.$watch(() => this.attrs.vertical_flip, this.onSizeChanged)
    this.$watch(() => this.attrs.rotate, this.onSizeChanged)
    this.$watch(() => this.attrs.scale_x, this.onSizeChanged)
    this.$watch(() => this.attrs.scale_y, this.onSizeChanged)
  },
}
</script>

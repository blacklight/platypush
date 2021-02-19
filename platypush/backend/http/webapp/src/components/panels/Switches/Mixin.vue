<script>
import Utils from "@/Utils";

export default {
  name: "SwitchesMixin",
  mixins: [Utils],

  props: {
    pluginName: {
      type: String,
      required: true,
    },

    bus: {
      type: Object,
      required: true,
    },

    config: {
      type: Object,
      default: () => { return {} },
    },

    selected: {
      type: Boolean,
      default: false,
    }
  },

  data() {
    return {
      loading: false,
      initialized: false,
      selectedDevice: null,
      devices: {},
    }
  },

  methods: {
    onRefreshEvent(pluginName) {
      if (pluginName !== this.pluginName)
        return

      this.refresh()
    },

    async toggle(device) {
      const response = await this.request(`${this.pluginName}.toggle`, {device: device})
      this.devices[device].on = response.on
    },

    async refresh() {
      this.loading = true
      try {
        this.devices = (await this.request(`${this.pluginName}.status`)).reduce((obj, device) => {
          const name = device.name?.length ? device.name : device.id
          obj[name] = device
          return obj
        }, {})
      } finally {
        this.loading = false
      }
    }
  },

  mounted() {
    this.$watch(() => this.selected, (newValue) => {
      if (newValue && !this.initialized) {
        this.refresh()
        this.initialized = true
      }
    })

    this.bus.on('refresh', this.onRefreshEvent)
  },

  unmounted() {
    this.bus.off('refresh', this.onRefreshEvent)
  },
}
</script>

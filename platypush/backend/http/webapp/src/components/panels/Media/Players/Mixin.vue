<script>
import Utils from "@/Utils";

export default {
  name: "Mixin",
  mixins: [Utils],
  emits: ['status'],

  props: {
    player: {
      type: Object,
    },
  },

  data() {
    return {
      iconClass: null,
      name: null,
      pluginName: null,
    }
  },

  methods: {
    async getPlayers() {
      return [{
        iconClass: this.iconClass,
        name: this.name,
        pluginName: this.pluginName,
        component: this,
        status: await this.status(),
      }]
    },

    async status() {
      return await this.request(`${this.pluginName}.status`)
    },

    async play(resource) {
      if (!resource) {
        return await this.pause()
      }

      return await this.request(`${this.pluginName}.play`, {resource: resource.url})
    },

    async pause() {
      return await this.request(`${this.pluginName}.pause`)
    },

    async stop() {
      return await this.request(`${this.pluginName}.stop`)
    },

    async setVolume(volume) {
      return await this.request(`${this.pluginName}.set_volume`, {volume: volume})
    },

    async seek(position) {
      return await this.request(`${this.pluginName}.seek`, {position: position})
    },

    async onNewMedia(event) {
      const isMine = await this.onMediaEvent(event)

      if (isMine && event.title) {
        this.notify({
          title: event.player || event.device || this.player?.name || this.name || this.pluginName,
          text: event.title,
          image: {
            iconClass: this.iconClass || 'fa fa-play',
          }
        })
      }
    },

    async onMediaEvent(event) {
      if (event.plugin !== this.pluginName)
        return false

      this.$emit('status', await this.status())
      return true
    },
  },

  mounted() {
    this.subscribe(this.onNewMedia, `on-new-media-${this.pluginName}`,
        'platypush.message.event.media.NewPlayingMediaEvent')

    this.subscribe(this.onMediaEvent, `on-media-event-${this.pluginName}`,
        'platypush.message.event.media.MediaPlayEvent',
        'platypush.message.event.media.MediaStopEvent',
        'platypush.message.event.media.MediaPauseEvent',
        'platypush.message.event.media.MediaSeekEvent',
        'platypush.message.event.media.MediaVolumeChangedEvent',
        'platypush.message.event.media.MediaMuteChangedEvent')
  },

  destroy() {
    this.unsubscribe(`on-media-event-${this.pluginName}`)
  },
}
</script>

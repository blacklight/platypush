<script>
import { bus } from "@/bus";

export default {
  name: "Events",
  computed: {
    _eventsReady() {
      return this.$root.$refs.events?.initialized
    },
  },

  methods: {
    subscribe(handler, ...events) {
      const subFunc = () => {
        bus.emit('subscribe', {
          events: events,
          handler: handler,
        })
      }

      if (this._eventsReady) {
        subFunc()
        return
      }

      const self = this
      const unwatch = this.$watch( () => self._eventsReady, (newVal) => {
        if (newVal) {
          subFunc()
          unwatch()
        }
      })
    },
  }
}
</script>

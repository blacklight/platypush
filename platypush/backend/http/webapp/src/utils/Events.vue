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
    subscribe(handler, handlerName, ...events) {
      const subFunc = () => {
        bus.emit('subscribe', {
          events: events,
          handler: handler,
          handlerName: handlerName || this.generateId(),
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

      return unwatch
    },

    unsubscribe(handlerName) {
      bus.emit('unsubscribe', handlerName)
    },

    generateId() {
      return btoa([...Array(16).keys()].forEach(() => String.fromCharCode(Math.round(Math.random() * 255))))
    },
  }
}
</script>

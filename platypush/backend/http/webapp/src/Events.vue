<template>
  <div id="__platypush_events"/>
</template>

<script>
export default {
  name: "Events",
  data() {
    return {
      ws: null,
      pending: false,
      opened: false,
      timeout: null,
      reconnectMsecs: 30000,
      handlers: [],
    }
  },

  methods: {
    init() {
      try {
        const protocol = location.protocol === 'https:' ? 'wss:' : 'ws'
        const url = `${protocol}://${location.hostname}:${this.$root.config.websocketPort}`
        this.ws = new WebSocket(url)
      } catch (err) {
        console.error('Websocket initialization error')
        console.log(err)
        return
      }

      this.pending = true

      const onWebsocketTimeout = function(self) {
        return function() {
          console.log('Websocket reconnection timed out, retrying')
          this.pending = false
          self.close()
          self.onclose()
        }
      }

      this.timeout = setTimeout(
          onWebsocketTimeout(this.ws), this.reconnectMsecs)

      this.ws.onmessage = (event) => {
        const handlers = []
        event = event.data

        if (typeof event === 'string') {
          try {
            event = JSON.parse(event)
          } catch (e) {
            console.warn('Received invalid non-JSON event')
            console.warn(event)
          }
        }

        console.debug(event)
        if (event.type !== 'event') {
          // Discard non-event messages
          return
        }

        if (null in this.handlers) {
          handlers.push(this.handlers[null])
        }

        if (event.args.type in this.handlers) {
          handlers.push(...this.handlers[event.args.type])
        }

        for (const handler of handlers) {
          handler(event.args)
        }
      }

      this.ws.onopen = () => {
        if (this.opened) {
          console.log("There's already an opened websocket connection, closing the newly opened one")
          this.onclose = () => {}
          this.close()
        }

        console.log('Websocket connection successful')
        this.opened = true

        if (this.pending) {
          this.pending = false
        }

        if (this.timeout) {
          clearTimeout(this.timeout)
          this.timeout = undefined
        }
      }

      this.ws.onerror = (event) => {
        console.error(event)
      }

      this.ws.onclose = (event) => {
        if (event) {
          console.log('Websocket closed - code: ' + event.code + ' - reason: ' + event.reason)
        }

        this.opened = false

        if (!this.pending) {
          this.pending = true
          this.init()
        }
      }
    }
  },

  mounted() {
    this.init()
  },
}
</script>

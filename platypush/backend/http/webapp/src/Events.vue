<script>
import { bus } from "@/bus";

export default {
  name: "Events",
  props: {
    wsPort: {
      type: Number,
      default: 8009,
    }
  },

  data() {
    return {
      ws: null,
      pending: false,
      opened: false,
      timeout: null,
      reconnectMsecs: 30000,
      handlers: {},
    }
  },

  methods: {
    onWebsocketTimeout() {
      return function() {
        console.log('Websocket reconnection timed out, retrying')
        this.pending = false
        this.close()
        this.onclose()
      }
    },

    onMessage(event) {
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

      for (let handler of handlers) {
        if (handler instanceof Array)
          handler = handler[0]

        handler(event.args)
      }
    },

    onOpen() {
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
    },

    onError(error) {
      console.error('Websocket error')
      console.error(error)
    },

    onClose(event) {
      if (event) {
        console.log('Websocket closed - code: ' + event.code + ' - reason: ' + event.reason)
      }

      this.opened = false

      if (!this.pending) {
        this.pending = true
        this.init()
      }
    },

    init() {
      try {
        const protocol = location.protocol === 'https:' ? 'wss:' : 'ws'
        const url = `${protocol}://${location.hostname}:${this.wsPort}`
        this.ws = new WebSocket(url)
      } catch (err) {
        console.error('Websocket initialization error')
        console.error(err)
        return
      }

      this.pending = true
      this.timeout = setTimeout(this.onWebsocketTimeout, this.reconnectMsecs)
      this.ws.onmessage = this.onMessage
      this.ws.onopen = this.onOpen
      this.ws.onerror = this.onError
      this.ws.onclose = this.onClose
    },

    subscribe(msg) {
      const handler = msg.handler
      const events = msg.events.length ? msg.events : [null]

      for (const event of events) {
        if (!(event in this.handlers)) {
          this.handlers[event] = []
        }

        this.handlers[event].push(handler)
      }
    },

    unsubscribe(msg) {
      const handler = msg.handler
      const events = msg.events.length ? msg.events : [null]

      for (const event of events) {
        if (!(event in this.handlers))
          continue

        const idx = this.handlers[event].indexOf(handler)
        if (idx < 0)
          continue

        this.handlers[event] = this.handlers[event].splice(idx, 1)[1]
        if (!this.handlers[event].length)
          delete this.handlers[event]
      }
    },
  },

  created() {
    bus.on('subscribe', this.subscribe)
    bus.on('unsubscribe', this.unsubscribe)
    this.init()
  },
}
</script>

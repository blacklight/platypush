<template>
  <div/>
</template>

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
      initialized: false,
      pending: false,
      opened: false,
      timeout: null,
      reconnectMsecs: 30000,
      handlers: {},
      handlerNameToEventTypes: {},
    }
  },

  methods: {
    onWebsocketTimeout() {
      console.log('Websocket reconnection timed out, retrying')
      this.pending = false
      if (this.ws)
        this.ws.close()

      this.onClose()
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
        handlers.push(...Object.values(this.handlers[event.args.type]))
      }

      for (let handler of handlers) {
        if (handler instanceof Array)
          handler = handler[0]
        else if (handler instanceof Object)
          handler = Object.values(handler)[0]

        handler(event.args)
      }
    },

    onOpen() {
      if (this.opened) {
        console.log("There's already an opened websocket connection, closing the newly opened one")
        if (this.ws) {
          this.ws.onclose = () => {}
          this.ws.close()
        }
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
        const protocol = location.protocol === 'https:' ? 'wss' : 'ws'
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
      this.initialized = true
    },

    subscribe(msg) {
      const handler = msg.handler
      const events = msg.events.length ? msg.events : [null]
      const handlerName = msg.handlerName

      for (const event of events) {
        if (!(event in this.handlers)) {
          this.handlers[event] = {}
        }

        if (!(handlerName in this.handlerNameToEventTypes)) {
          this.handlerNameToEventTypes[handlerName] = events
        }

        this.handlers[event][handlerName] = handler
      }

      return () => {
        this.unsubscribe(handlerName)
      }
    },

    unsubscribe(handlerName) {
      const events = this.handlerNameToEventTypes[handlerName]
      if (!events)
        return

      for (const event of events) {
        if (!this.handlers[event]?.[handlerName])
          continue

        delete this.handlers[event][handlerName]
        if (!Object.keys(this.handlers[event]).length)
          delete this.handlers[event]
      }

      delete this.handlerNameToEventTypes[handlerName]
    },
  },

  created() {
    bus.on('subscribe', this.subscribe)
    bus.on('unsubscribe', this.unsubscribe)
    this.init()
  },
}
</script>

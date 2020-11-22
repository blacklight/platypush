<script>
import { bus } from "@/bus";

export default {
  name: "Events",
  methods: {
    subscribe(handler, ...events) {
      bus.emit('subscribe', {
        events: events,
        handler: handler,
      })
    },
  }
}
</script>

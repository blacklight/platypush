<script>
import { bus } from "@/bus";

export default {
  name: "Notification",
  methods: {
    notify(notification) {
      bus.emit('notification-create', notification)
    },

    warn(msg) {
      this.notify({
        text: msg,
        warning: true,
      })
    },

    error(msg) {
      this.notify({
        text: msg,
        error: true,
      })

      throw msg
    },
  }
}
</script>

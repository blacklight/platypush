<script>
import { bus } from "@/bus";

export default {
  name: "Notification",
  methods: {
    notify(notification) {
      bus.publishNotification(notification)
    },

    notifyWarning(msg) {
      this.notify({
        text: msg,
        warning: true,
      })
    },

    notifyError(msg) {
      this.notify({
        text: msg,
        error: true,
      })

      throw msg
    },
  }
}
</script>

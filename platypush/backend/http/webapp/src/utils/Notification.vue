<script>
import { bus } from '@/bus';

export default {
  name: "Notification",
  methods: {
    notify(notification) {
      bus.emit('notification-create', notification)
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

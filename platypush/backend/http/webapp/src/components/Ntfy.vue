<template>
  <div />
</template>

<script>
import Utils from "@/Utils";

export default {
  name: "Ntfy",
  mixins: [Utils],

  methods: {
    onMessage(event) {
      this.notify({
        title: event.title,
        text: event.message,
        image: {
          icon: 'bell',
        },
      })
    },
  },

  mounted() {
    this.subscribe(this.onMessage, null, 'platypush.message.event.ntfy.NotificationEvent')
  },
}
</script>

<template>
  <div />
</template>

<script>
import Utils from "@/Utils";

export default {
  mixins: [Utils],

  methods: {
    onMessage(event) {
      this.notify({
        title: event.title,
        text: event.body,
        image: {
          src: event.icon ? 'data:image/png;base64, ' + event.icon : undefined,
          icon: event.icon ? undefined : 'bell',
        },
      })
    },
  },

  mounted() {
    this.subscribe(
      this.onMessage,
      null,
      'platypush.message.event.pushbullet.PushbulletNotificationEvent'
    )
  },
}
</script>

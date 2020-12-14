<template>
  <div />
</template>

<script>
import Utils from "@/Utils";

export default {
  name: "Pushbullet",
  mixins: [Utils],

  methods: {
    onMessage(event) {
      if (event.push_type === 'mirror') {
        this.notify({
          title: event.title,
          text: event.body,
          image: {
            src: event.icon ? 'data:image/png;base64, ' + event.icon : undefined,
            icon: event.icon ? undefined : 'bell',
          },
        });
      }
    },
  },

  mounted() {
    this.subscribe(this.onMessage, null, 'platypush.message.event.pushbullet.PushbulletEvent')
  },
}
</script>

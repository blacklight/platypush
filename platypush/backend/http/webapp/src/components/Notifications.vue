<template>
  <div class="notifications">
    <Notification v-for="(notification, id, index) in notifications"
                  :key="index"
                  :id="id"
                  :text="notification.text"
                  :html="notification.html"
                  :title="notification.title"
                  :link="notification.link"
                  :image="notification.image"
                  :warning="notification.warning"
                  :error="notification.error"
                  @clicked="destroy">
    </Notification>
  </div>
</template>

<script>
import Notification from "@/components/Notification";

export default {
  name: "Notifications",
  components: {Notification},
  props: {
    duration: {
      // Default notification duration in milliseconds
      type: Number,
      default: 10000,
    }
  },

  data: function() {
    return {
      index: 0,
      notifications: {},
      timeouts: {},
    };
  },

  methods: {
    create: function(args) {
      const id = this.index++;
      this.notifications[id] = args;

      if (args.duration == null) {
        args.duration = this.duration;
      }

      const duration = args.duration ? parseInt(args.duration) : 0;
      if (duration) {
        this.timeouts[id] = setTimeout(this.destroy.bind(null, id), duration);
      }
    },

    destroy: function(id) {
      delete this.notifications[id];
      delete this.timeouts[id];
    },
  },
}
</script>

<style scoped>
.notifications {
  position: fixed;
  bottom: 0;
  right: 0;
  width: 25em;
  z-index: 1000;
}
</style>
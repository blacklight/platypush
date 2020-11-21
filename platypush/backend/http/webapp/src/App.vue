<template>
  <router-view />
  <Notifications ref="notifications" />
  <Events ref="events" />
</template>

<script>
import Notifications from "@/components/Notifications";
import Utils from "@/Utils";
import { bus } from '@/bus';
import Events from "@/Events";

export default {
  name: 'App',
  components: {Events, Notifications},
  mixins: [Utils],

  computed: {
    config() {
      const cfg = {
        websocketPort: 8009,
      }

      if (this._config.websocketPort && !this._config.websocketPort.startsWith('{{')) {
        cfg.websocketPort = parseInt(this._config.websocketPort)
      }

      return cfg;
    }
  },

  methods: {
    onNotification(notification) {
      this.$refs.notifications.create(notification)
    }
  },

  mounted() {
    bus.on('notification-create', this.onNotification)
  }
}
</script>

<!--suppress CssUnusedSymbol -->
<style lang="scss">
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
@import "~@fortawesome/fontawesome-free/scss/fontawesome";
@import "~@fortawesome/fontawesome-free/scss/solid";    // fas
@import "~@fortawesome/fontawesome-free/scss/regular";  // far
@import "~@fortawesome/fontawesome-free/scss/brands";   // fab

html, body {
  width: 100%;
  height: 100%;
  margin: 0;
  overflow: auto;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  width: 100%;
  height: 100%;
  color: #2c3e50;
}
</style>

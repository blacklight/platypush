<template>
  <Events ref="events" :ws-port="config['backend.http'].websocket_port"
          v-if="Object.keys(config).length && config['backend.http']" />

  <Notifications ref="notifications" />
  <VoiceAssistant ref="voice-assistant" v-if="Object.keys(config).length" />
  <router-view />
</template>

<script>
import Notifications from "@/components/Notifications";
import Utils from "@/Utils";
import Events from "@/Events";
import VoiceAssistant from "@/components/VoiceAssistant";
import { bus } from "@/bus";

export default {
  name: 'App',
  mixins: [Utils],
  components: {Notifications, Events, VoiceAssistant},

  data() {
    return {
      config: {},
    }
  },

  methods: {
    onNotification(notification) {
      this.$refs.notifications.create(notification)
    },

    async initConfig() {
      this.config = await this.request('config.get')
    }
  },

  created() {
    this.initConfig()
  },

  mounted() {
    bus.on('notification-create', this.onNotification)
  },
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

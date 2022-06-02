<template>
  <Events ref="events" :ws-port="config['backend.http'].websocket_port" v-if="hasWebsocket" />
  <Notifications ref="notifications" />
  <VoiceAssistant ref="voice-assistant" v-if="hasAssistant" />
  <Pushbullet ref="pushbullet" v-if="hasPushbullet" />
  <Ntfy ref="ntfy" v-if="hasNtfy" />

  <router-view />
</template>

<script>
import Notifications from "@/components/Notifications";
import Utils from "@/Utils";
import Events from "@/Events";
import VoiceAssistant from "@/components/VoiceAssistant";
import { bus } from "@/bus";
import Ntfy from "@/components/Ntfy";
import Pushbullet from "@/components/Pushbullet";

export default {
  name: 'App',
  mixins: [Utils],
  components: {
    Pushbullet, Ntfy, Notifications, Events, VoiceAssistant
  },

  data() {
    return {
      config: {},
      userAuthenticated: false,
    }
  },

  computed: {
    hasWebsocket() {
      return this.userAuthenticated &&
          'backend.http' in this.config
    },

    hasAssistant() {
      return this.hasWebsocket
    },

    hasPushbullet() {
      return this.hasWebsocket && (
          'pushbullet' in this.config ||
          'backend.pushbullet' in this.config
      )
    },

    hasNtfy() {
      return this.hasWebsocket && 'ntfy' in this.config
    },
  },

  methods: {
    onNotification(notification) {
      this.$refs.notifications.create(notification)
    },

    async initConfig() {
      this.config = await this.request('config.get')
      this.userAuthenticated = true
    },
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
  font-family: BlinkMacSystemFont,-apple-system,Avenir,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Fira Sans,Droid Sans,Helvetica Neue,Helvetica,Verdana,Arial,sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  width: 100%;
  height: 100%;
  color: #2c3e50;
}
</style>

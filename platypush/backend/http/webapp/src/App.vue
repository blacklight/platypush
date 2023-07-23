<template>
  <Events ref="events" v-if="hasWebsocket" />
  <Notifications ref="notifications" />
  <VoiceAssistant ref="voice-assistant" v-if="hasAssistant" />
  <Pushbullet ref="pushbullet" v-if="hasPushbullet" />
  <Ntfy ref="ntfy" v-if="hasNtfy" />
  <ConfirmDialog ref="pwaDialog" @input="installPWA">
    Would you like to install this application locally?
  </ConfirmDialog>

  <router-view />
</template>

<script>
import ConfirmDialog from "@/components/elements/ConfirmDialog";
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
    ConfirmDialog, Pushbullet, Ntfy, Notifications, Events, VoiceAssistant
  },

  data() {
    return {
      config: {},
      userAuthenticated: false,
      pwaInstallEvent: null,
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
      this.config = await this.request('config.get', {}, 60000, false)
      this.userAuthenticated = true
    },

    installPWA() {
      if (this.pwaInstallEvent)
        this.pwaInstallEvent.prompt()

      this.$refs.pwaDialog.close()
    }
  },

  created() {
    this.initConfig()
  },

  beforeMount() {
    if (this.getCookie('pwa-dialog-shown')?.length)
      return

    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault()
      this.pwaInstallEvent = e
      this.$refs.pwaDialog.show()

      this.setCookie('pwa-dialog-shown', '1', {
        expires: new Date(new Date().getTime() + 365 * 24 * 60 * 60 * 1000)
      })
    })
  },

  mounted() {
    bus.onNotification(this.onNotification)
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

<template>
  <Events ref="events" :ws-port="config['backend.http'].websocket_port" v-if="config['backend.http']" />
  <Notifications ref="notifications" />
</template>

<script>
import Events from "@/Events";
import Notifications from "@/components/Notifications";

export default {
  name: "Base",
  components: {Events, Notifications}
}
</script>


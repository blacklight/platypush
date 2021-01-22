<template>
  <div class="info">
    <div class="row" v-if="info?.server?.host?.ip?.length">
      <div class="label col-3">IP Address</div>
      <div class="value col-9" v-text="info.server.host.ip"></div>
    </div>

    <div class="row" v-if="info?.server?.host?.mac?.length">
      <div class="label col-3">MAC Address</div>
      <div class="value col-9" v-text="info.server.host.mac"></div>
    </div>

    <div class="row" v-if="info?.server?.host?.name?.length">
      <div class="label col-3">Name</div>
      <div class="value col-9" v-text="info.server.host.name"></div>
    </div>

    <div class="row" v-if="info?.server?.host?.port">
      <div class="label col-3">Port</div>
      <div class="value col-9" v-text="info.server.host.port"></div>
    </div>

    <div class="row" v-if="info?.server?.host?.os?.length">
      <div class="label col-3">OS</div>
      <div class="value col-9" v-text="info.server.host.os"></div>
    </div>

    <div class="row" v-if="info?.server?.host?.arch?.length">
      <div class="label col-3">Architecture</div>
      <div class="value col-9" v-text="info.server.host.arch"></div>
    </div>

    <div class="row" v-if="info?.server?.snapserver?.name?.length">
      <div class="label col-3">Server name</div>
      <div class="value col-9" v-text="info.server.snapserver.name"></div>
    </div>

    <div class="row" v-if="info?.server?.snapserver?.version?.length">
      <div class="label col-3">Server version</div>
      <div class="value col-9" v-text="info.server.snapserver.version"></div>
    </div>

    <div class="row" v-if="info?.server?.snapserver?.protocolVersion">
      <div class="label col-3">Protocol version</div>
      <div class="value col-9" v-text="info.server.snapserver.protocolVersion"></div>
    </div>

    <div class="row" v-if="info?.server?.snapserver?.controlProtocolVersion">
      <div class="label col-3">Control protocol version</div>
      <div class="value col-9" v-text="info.server.snapserver.controlProtocolVersion"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: "HostModal",
  props: {
    info: {
      type: Object,
      default: () => {},
    }
  }
}
</script>

<style scoped>

</style>
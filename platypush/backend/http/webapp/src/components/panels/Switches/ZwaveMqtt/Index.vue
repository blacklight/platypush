<template>
  <div class="switches zwave-mqtt-switches">
    <Loading v-if="loading" />
    <div class="no-content" v-else-if="!Object.keys(devices).length">No Z-Wave switches found.</div>

    <Switch :loading="loading" :name="name" :state="device.on" :id="device.id" @toggle="toggle(name, device.id)"
            v-for="(device, name) in devices" :key="name" />
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import SwitchMixin from "@/components/panels/Switches/Mixin";
import Switch from "@/components/panels/Switches/Switch";

export default {
  name: "ZwaveMqtt",
  components: {Switch, Loading},
  mixins: [SwitchMixin],
}
</script>

<style lang="scss" scoped>
@import "../common";
</style>

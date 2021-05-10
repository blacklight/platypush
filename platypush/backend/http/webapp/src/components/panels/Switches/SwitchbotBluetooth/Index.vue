<template>
  <div class="switches switchbot-switches">
    <Loading v-if="loading" />
    <div class="no-content" v-else-if="!Object.keys(devices).length">No SwitchBot switches found.</div>

    <Switch :loading="loading" :name="name" :state="device.on" @toggle="toggle(name)"
            v-for="(device, name) in devices" :key="name" :has-info="true"
            @info="selectedDevice = name; $refs.switchInfoModal.show()" />

    <Modal title="Device Info" ref="switchInfoModal">
      <div class="switch-info" v-if="selectedDevice">
        <div class="row">
          <div class="name">Name</div>
          <div class="value" v-text="devices[selectedDevice].name" />
        </div>

        <div class="row">
          <div class="name">On</div>
          <div class="value" v-text="devices[selectedDevice].on" />
        </div>

        <div class="row">
          <div class="name">Address</div>
          <div class="value" v-text="devices[selectedDevice].address" />
        </div>
      </div>
    </Modal>
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import SwitchMixin from "@/components/panels/Switches/Mixin";
import Switch from "@/components/panels/Switches/Switch";
import Modal from "@/components/Modal";

export default {
  name: "SwitchbotBluetooth",
  components: {Modal, Switch, Loading},
  mixins: [SwitchMixin],
}
</script>

<style lang="scss" scoped>
@import "../common";
</style>

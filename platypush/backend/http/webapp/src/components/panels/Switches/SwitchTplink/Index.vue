<template>
  <div class="switches tplink-switches">
    <Loading v-if="loading" />
    <div class="no-content" v-else-if="!Object.keys(devices).length">No TP-Link switches found.</div>

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
          <div class="name">IP</div>
          <div class="value" v-text="devices[selectedDevice].ip" />
        </div>

        <div class="row" v-if="devices[selectedDevice].hw_info?.mac">
          <div class="name">MAC</div>
          <div class="value" v-text="devices[selectedDevice].hw_info.mac" />
        </div>

        <div class="row" v-if="devices[selectedDevice].current_consumption != null">
          <div class="name">Current Consumption</div>
          <div class="value" v-text="devices[selectedDevice].current_consumption" />
        </div>

        <div class="row" v-if="devices[selectedDevice].hw_info?.dev_name">
          <div class="name">Device Type</div>
          <div class="value" v-text="devices[selectedDevice].hw_info.dev_name" />
        </div>

        <div class="row" v-if="devices[selectedDevice].hw_info?.fwId">
          <div class="name">Firmware ID</div>
          <div class="value" v-text="devices[selectedDevice].hw_info.fwId" />
        </div>

        <div class="row" v-if="devices[selectedDevice].hw_info?.hwId">
          <div class="name">Hardware ID</div>
          <div class="value" v-text="devices[selectedDevice].hw_info.hwId" />
        </div>

        <div class="row" v-if="devices[selectedDevice].hw_info?.hw_ver">
          <div class="name">Hardware Version</div>
          <div class="value" v-text="devices[selectedDevice].hw_info.hw_ver" />
        </div>

        <div class="row" v-if="devices[selectedDevice].hw_info?.sw_ver">
          <div class="name">Software Version</div>
          <div class="value" v-text="devices[selectedDevice].hw_info.sw_ver" />
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
  name: "SwitchTplink",
  components: {Modal, Switch, Loading},
  mixins: [SwitchMixin],
}
</script>

<style lang="scss" scoped>
@import "../common";
</style>

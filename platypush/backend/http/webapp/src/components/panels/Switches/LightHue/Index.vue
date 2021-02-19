<template>
  <div class="switches switchbot-switches">
    <Loading v-if="loading" />
    <div class="no-content" v-else-if="!Object.keys(devices).length">No Hue lights found.</div>

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

        <div class="row" v-if="devices[selectedDevice].reachable != null">
          <div class="name">Reachable</div>
          <div class="value" v-text="devices[selectedDevice].reachable" />
        </div>

        <div class="row" v-if="devices[selectedDevice].bri != null">
          <div class="name">Brightness</div>
          <div class="value" v-text="devices[selectedDevice].bri" />
        </div>

        <div class="row" v-if="devices[selectedDevice].ct != null">
          <div class="name">Color Temperature</div>
          <div class="value" v-text="devices[selectedDevice].ct" />
        </div>

        <div class="row" v-if="devices[selectedDevice].hue != null">
          <div class="name">Hue</div>
          <div class="value" v-text="devices[selectedDevice].hue" />
        </div>

        <div class="row" v-if="devices[selectedDevice].sat != null">
          <div class="name">Saturation</div>
          <div class="value" v-text="devices[selectedDevice].sat" />
        </div>

        <div class="row" v-if="devices[selectedDevice].xy != null">
          <div class="name">XY</div>
          <div class="value" v-text="`[${devices[selectedDevice].xy.join(', ')}]`" />
        </div>

        <div class="row" v-if="devices[selectedDevice].productname != null">
          <div class="name">Product</div>
          <div class="value" v-text="devices[selectedDevice].productname" />
        </div>

        <div class="row" v-if="devices[selectedDevice].manufacturername != null">
          <div class="name">Manufacturer</div>
          <div class="value" v-text="devices[selectedDevice].manufacturername " />
        </div>

        <div class="row" v-if="devices[selectedDevice].type != null">
          <div class="name">Type</div>
          <div class="value" v-text="devices[selectedDevice].type " />
        </div>

        <div class="row" v-if="devices[selectedDevice].id != null">
          <div class="name">ID on network</div>
          <div class="value" v-text="devices[selectedDevice].id " />
        </div>

        <div class="row" v-if="devices[selectedDevice].uniqueid != null">
          <div class="name">Unique ID</div>
          <div class="value" v-text="devices[selectedDevice].uniqueid " />
        </div>

        <div class="row" v-if="devices[selectedDevice].swversion != null">
          <div class="name">Software version</div>
          <div class="value" v-text="devices[selectedDevice].swversion " />
        </div>

        <div class="row" v-if="devices[selectedDevice].swupdate?.lastinstall">
          <div class="name">Last software update</div>
          <div class="value" v-text="formatDate(devices[selectedDevice].swupdate.lastinstall, true)" />
        </div>

        <div class="row" v-if="devices[selectedDevice].swupdate?.state">
          <div class="name">Update state</div>
          <div class="value" v-text="devices[selectedDevice].swupdate.state" />
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
  name: "LightHue",
  components: {Modal, Switch, Loading},
  mixins: [SwitchMixin],

  methods: {
    async toggle(device) {
      const response = await this.request(`${this.pluginName}.toggle`, {lights: [device]})
      if (response.success)
        this.devices[device].on = !this.devices[device].on
    },
  }
}
</script>

<style lang="scss" scoped>
@import "../common";
</style>

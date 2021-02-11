<template>
  <div class="zigbee-container">
    <Loading v-if="loading" />

    <Modal title="Network Info" ref="infoModal">
      <div class="info-body" v-if="status.info">
        <div class="row">
          <div class="param-name">State</div>
          <div class="param-value" v-text="status.state" />
        </div>

        <div class="row">
          <div class="param-name">Permit Join</div>
          <div class="param-value" v-text="status.info.permit_join" />
        </div>

        <div class="row" v-if="status.info.network">
          <div class="param-name">Network Channel</div>
          <div class="param-value" v-text="status.info.network.channel" />
        </div>

        <div class="row">
          <div class="param-name">Zigbee2MQTT Version</div>
          <div class="param-value" v-text="status.info.version" />
        </div>

        <div class="row" v-if="status.info.config?.mqtt">
          <div class="param-name">MQTT Server</div>
          <div class="param-value" v-text="status.info.config.mqtt.server" />
        </div>

        <div class="row" v-if="status.info.config?.serial">
          <div class="param-name">Serial Port</div>
          <div class="param-value" v-text="status.info.config.serial.port" />
        </div>

        <div class="row" v-if="status.info.coordinator?.type">
          <div class="param-name">Firmware Type</div>
          <div class="param-value" v-text="status.info.coordinator.type" />
        </div>

        <div class="row" v-if="status.info.coordinator?.meta">
          <div class="param-name">Firmware Version</div>
          <div class="param-value">
            {{ status.info.coordinator.meta.maintrel }}.{{ status.info.coordinator.meta.majorrel }}.{{ status.info.coordinator.meta.minorrel }}
          </div>
        </div>

        <div class="row" v-if="status.info.coordinator?.meta">
          <div class="param-name">Firmware Revision</div>
          <div class="param-value" v-text="status.info.coordinator.meta.revision" />
        </div>
      </div>
    </Modal>

    <div class="view-options">
      <div class="view-selector col-s-8 col-m-9 col-l-10">
        <label>
          <select :value="selected.view" @change="this.selected.view = $event.target.value">
            <option v-for="(enabled, view) in views"
                    v-text="(view[0].toUpperCase() + view.slice(1)).replace('_', ' ')"
                    :key="view" :selected="enabled" :value="view">
            </option>
          </select>
        </label>
      </div>

      <div class="buttons">
        <button class="btn btn-default" title="Add Group" v-if="selected.view === 'groups'"
                :disabled="loading" @click="addGroup">
          <i class="fa fa-plus"></i>
        </button>

        <Dropdown ref="networkCommandsDropdown" icon-class="fa fa-cog" title="Network commands">
          <DropdownItem text="Network Info" :disabled="loading" @click="$refs.infoModal.show()" />
          <DropdownItem text="Permit Join" :disabled="loading" @click="permitJoin(true)"
                        v-if="!status.info?.permit_join" />
          <DropdownItem text="Disable Join" :disabled="loading" @click="permitJoin(false)" v-else/>
          <DropdownItem text="Factory Reset" :disabled="loading" @click="factoryReset" />
        </Dropdown>

        <button class="btn btn-default" title="Refresh network" :disabled="loading" @click="refresh">
          <i class="fa fa-sync-alt"></i>
        </button>
      </div>
    </div>

    <div class="view-container">
      <div class="view devices" v-if="selected.view === 'devices'">
        <div class="no-items" v-if="!Object.keys(devices).length">
          <div class="loading" v-if="loading">Loading devices...</div>
          <div class="empty" v-else>No devices found on the network</div>
        </div>

        <Device v-for="(device, id) in devices" :key="id"
                :device="device" :groups="groups" :selected="selected.deviceId === id"
                @select="selected.deviceId = selected.deviceId === id ? null : id"
                @rename="refreshDevices" @remove="refreshDevices" @groups-edit="refreshGroups" />
      </div>

      <div class="view groups" v-else-if="selected.view === 'groups'">
        <div class="no-items" v-if="!Object.keys(groups).length">
          <div class="loading" v-if="loading">Loading groups...</div>
          <div class="empty" v-else>No groups available on the network</div>
        </div>

        <Group v-for="(group, id) in groups" :key="id" :group="group" :devices="devices"
               :selected="selected.groupId === id"
               @select="selected.groupId = selected.groupId === id ? null : id"
               @rename="refreshGroups" @remove="refreshGroups" @edit="refreshGroups" />
      </div>
    </div>
  </div>
</template>

<script>
import Dropdown from "../../elements/Dropdown"
import DropdownItem from "@/components/elements/DropdownItem"
import Loading from "@/components/Loading"
import Utils from "@/Utils"

import Device from "@/components/panels/ZigbeeMqtt/Device";
import Group from "@/components/panels/ZigbeeMqtt/Group";
import Modal from "@/components/Modal";

export default {
  name: "ZigbeeMqtt",
  components: {Modal, Dropdown, DropdownItem, Loading, Device, Group},
  mixins: [Utils],

  data() {
    return {
      devices: {},
      groups: {},
      status: {},
      loading: false,
      selected: {
        view: 'devices',
        deviceId: undefined,
        groupId: undefined,
      },
      views: {
        devices: true,
        groups: true,
      },
      modal: {
        group: {
          visible: false,
        },
      },
    }
  },

  methods: {
    async refreshDevices() {
      this.loading = true

      try {
        this.devices = (await this.request('zigbee.mqtt.devices')).reduce((devices, device) => {
          if (device.friendly_name in this.devices) {
            device = {
              values: this.devices[device.friendly_name].values || {},
              ...this.devices[device.friendly_name],
            }
          }

          devices[device.friendly_name] = device
          return devices
        }, {})
      } finally {
        this.loading = false
      }
    },

    async refreshGroups() {
      this.loading = true
      try {
        this.groups = (await this.request('zigbee.mqtt.groups')).reduce((groups, group) => {
          groups[group.id] = group
          return groups
        }, {})
      } finally {
        this.loading = false
      }
    },

    async refreshInfo() {
      this.loading = true
      try {
        this.status = await this.request('zigbee.mqtt.info')
      } finally {
        this.loading = false
      }
    },

    refresh() {
      this.refreshDevices()
      this.refreshGroups()
      this.refreshInfo()
    },

    updateProperties(device, props) {
      this.devices[device].values = props
    },

    async addGroup() {
      const name = prompt('Group name')
      if (!(name && name.length)) {
        return
      }

      this.loading = true
      try {
        await this.request('zigbee.mqtt.group_add', {name: name})
      } finally {
        this.loading = false
      }

      await this.refreshGroups()
    },

    async permitJoin(permit) {
      const args = {permit: !!permit}
      if (permit) {
        let seconds = prompt('Join allow period in seconds (0 or empty for no time limits)', '60')
        args.seconds = seconds.length ? parseInt(seconds) : null
      }

      this.loading = true
      try {
        await this.request('zigbee.mqtt.permit_join', args)
        setTimeout(this.refreshInfo, 1000)
      } finally {
        this.loading = false
      }
    },

    async factoryReset() {
      if (!confirm('Are you SURE that you want to do a device factory reset?')) {
        if (!confirm('Are you REALLY sure? ALL network information and custom firmware will be lost!!'))
          return
      }

      this.loading = true
      try {
        await this.request('zigbee.mqtt.factory_reset')
      } finally {
        this.loading = false
      }
    },

    async addToGroup(device, group) {
      this.loading = true
      await this.request('zigbee.mqtt.group_add_device', {
        device: device,
        group: group,
      })

      this.loading = false
      const self = this

      setTimeout(() => {
        self.refresh()
        self.refreshGroups()
      }, 100)
    },
  },

  created() {
    this.subscribe(() => {
      this.notify({
        text: 'WARNING: The controller is offline',
        error: true,
      })
    }, 'on-zigbee-offline', 'platypush.message.event.zigbee.mqtt.ZigbeeMqttOfflineEvent')

    this.subscribe(() => {
      this.notify({
        text: 'The controller is now online',
        iconClass: 'fas fa-check',
      })
    }, 'on-zigbee-online', 'platypush.message.event.zigbee.mqtt.ZigbeeMqttOnlineEvent')

    this.subscribe(() => {
      this.notify({
        text: 'Failed to remove the device',
        error: true,
      })
    }, 'on-zigbee-device-remove-failed', 'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceRemovedFailedEvent')

    this.subscribe(() => {
      this.notify({
        text: 'Failed to add the group',
        error: true,
      })
    }, 'on-zigbee-group-add-failed', 'platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupAddedFailedEvent')

    this.subscribe(() => {
      this.notify({
        text: 'Failed to remove group',
        error: true,
      })
    }, 'on-zigbee-group-remove-failed', 'platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupRemovedFailedEvent')

    this.subscribe(() => {
      this.notify({
        text: 'Failed to remove the devices from group',
        error: true,
      })
    }, 'on-zigbee-remove-all-failed',
        'platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupRemoveAllFailedEvent')

    this.subscribe((event) => {
      this.notify({
        text: event.error || '[Unknown error]',
        error: true,
      })
    }, 'on-zigbee-error', 'platypush.message.event.zigbee.mqtt.ZigbeeMqttErrorEvent')

    this.subscribe(this.refresh, 'on-zigbee-device-update',
        'platypush.message.event.zigbee.mqtt.ZigbeeMqttOnlineEvent',
        'platypush.message.event.zigbee.mqtt.ZigbeeMqttDevicePairingEvent',
        'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceConnectedEvent',
        'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceBannedEvent',
        'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceRemovedEvent',
        'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceWhitelistedEvent',
        'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceRenamedEvent',
        'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceBindEvent',
        'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceUnbindEvent',
    )

    this.subscribe(this.refreshGroups, 'on-zigbee-group-update',
        'platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupAddedEvent',
        'platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupRemovedEvent',
        'platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupRemoveAllEvent',
    )
  },

  mounted() {
    this.refresh()
  },

  unmounted() {
    this.unsubscribe('on-zigbee-error')
    this.unsubscribe('on-zigbee-remove-all-failed')
    this.unsubscribe('on-zigbee-group-remove-failed')
    this.unsubscribe('on-zigbee-group-add-failed')
    this.unsubscribe('on-zigbee-device-remove-failed')
    this.unsubscribe('on-zigbee-online')
    this.unsubscribe('on-zigbee-offline')
    this.unsubscribe('on-zigbee-device-update')
    this.unsubscribe('on-zigbee-group-update')
  },
}
</script>

<style lang="scss">
@import "common";

.zigbee-container {
  width: 100%;
  height: 100%;
  padding: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: auto;

  .no-items {
    padding: 2em;
    font-size: 1.5em;
    color: $no-items-color;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .view-options {
    display: flex;
    width: 100%;
    height: $header-height;
    justify-content: space-between;
    align-items: center;
    padding: 0;
    background: $header-bg;
    border-bottom: $default-border-2;
    box-shadow: $border-shadow-bottom;

    .view-selector {
      display: inline-flex;
      padding-left: .5em;

      label {
        width: 100%;
      }
    }

    .buttons {
      display: inline-flex;
      margin: 0;

      button {
        background: none;
        border: none;
        padding: 0 .75em;

        &:hover {
          color: $default-hover-fg;
        }
      }

      .dropdown {
        .item {
          padding: .5em 2em .5em .5em;
        }
      }
    }
  }

  .view-container {
    width: 100%;
    height: calc(100% - #{$header-height});
    display: flex;
    justify-content: center;
    overflow: auto;
  }

  .view {
    height: max-content;
    background: $view-bg;
    border: $view-border;
    box-shadow: $view-box-shadow;
  }

  @media screen and (max-width: $tablet) {
    .view {
      width: 100%;
    }
  }

  @media screen and (min-width: $tablet) {
    .view {
      width: 100%;
    }
  }

  @media screen and (min-width: $desktop) {
    .view {
      min-width: 400pt;
      max-width: 750pt;
      border-radius: 1.5em;
    }

    .view-container {
      padding-top: 2em;
    }
  }

  .params {
    background: $params-bg;
    padding-bottom: 1em;

    .section {
      display: flex;
      flex-direction: column;
      padding: 0 1em;

      &:not(:first-child) {
        padding-top: 1em;
      }

      .header {
        display: flex;
        align-items: center;
        font-weight: bold;
        border-bottom: $param-section-header-border;
      }
    }

  }

  .btn-value-name-edit {
    padding: 0;
  }

  .modal {
    .section {
      .header {
        background: none;
        padding: .5em 0;
      }

      .body {
        padding: 0;
      }
    }

    .network-info {
      min-width: 600pt;
    }
  }

  .error {
    color: $error-color;
  }

  .device, .group {
    .actions {
      .row {
        cursor: pointer;
      }
    }

    form {
      margin-bottom: 0;
    }

    .param-value {
      input[type=text] {
        text-align: right;
      }
    }
  }

  .info-body {
    margin: -2em;
    padding: 0;

    .row {
      padding: 1em .5em;

      .param-name {
        font-weight: bold;
      }
    }
  }

  @media screen and (max-width: $tablet) {
    .info-body {
      width: 100vw;
    }
  }

  @media screen and (min-width: $tablet) {
    .info-body {
      width: 80vw;
    }
  }

  @media screen and (min-width: $desktop) {
    .info-body {
      width: 60vw;
      max-width: 30em;
    }
  }
}
</style>

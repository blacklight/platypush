<template>
  <div class="zigbee-container">
    <Loading v-if="loading" />

    <!-- Include group modal -->

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
          <DropdownItem text="Permit Join" :disabled="loading" @click="permitJoin(true)" />
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
                :device="device" :selected="selected.deviceId === id"
                @select="selected.deviceId = selected.deviceId === id ? null : id"
                @rename="refreshDevices" @remove="refreshDevices" />

        <!--      <dropdown ref="addToGroupDropdown" :items="addToGroupDropdownItems"></dropdown>-->
      </div>

      <div class="view groups" v-else-if="selected.view === 'groups'">
        <div class="no-items" v-if="!Object.keys(groups).length">
          <div class="loading" v-if="loading">Loading groups...</div>
          <div class="empty" v-else>No groups available on the network</div>
        </div>

        <Group v-for="(group, id) in groups" :key="id" :group="group"
               :selected="selected.groupId === id"
               @select="selected.groupId = selected.groupId === id ? null : id"
               @rename="refreshGroups" @remove="refreshGroups" />
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

export default {
  name: "ZigbeeMqtt",
  components: {Dropdown, DropdownItem, Loading, Device, Group},
  mixins: [Utils],

  data() {
    return {
      status: {},
      devices: {},
      groups: {},
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

  computed: {
    // addToGroupDropdownItems: function() {
    //   const self = this
    //   return Object.values(this.groups).filter((group) => {
    //     return !group.values || !group.values.length || !(this.selected.valueId in this.scene.values)
    //   }).map((group) => {
    //     return {
    //       text: group.name,
    //       disabled: this.loading,
    //       click: async function () {
    //         if (!self.selected.valueId) {
    //           return
    //         }
    //
    //         self.loading = true
    //         await this.request('zwave.scene_add_value', {
    //           id_on_network: self.selected.valueId,
    //           scene_id: group.scene_id,
    //         })
    //
    //         self.loading = false
    //         self.refresh()
    //       },
    //     }
    //   })
    // },
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
      this.groups = (await this.request('zigbee.mqtt.groups')).reduce((groups, group) => {
        groups[group.id] = group
        return groups
      }, {})

      this.loading = false
    },

    refresh() {
      this.refreshDevices()
      this.refreshGroups()
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

    async startNetwork() {
      this.loading = true
      try {
        await this.request('zigbee.mqtt.start_network')
      } finally {
        this.loading = false
      }
    },

    async stopNetwork() {
      this.loading = true
      try {
        await this.request('zigbee.mqtt.stop_network')
      } finally {
        this.loading = false
      }
    },

    async permitJoin(permit) {
      let seconds = prompt('Join allow period in seconds (0 or empty for no time limits)', '60')
      seconds = seconds.length ? parseInt(seconds) : null
      this.loading = true

      try {
        await this.request('zigbee.mqtt.permit_join', {permit: !!permit, timeout: seconds || null})
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

    // openAddToGroupDropdown(event) {
    //   this.selected.valueId = event.valueId
    //   openDropdown(this.$refs.addToGroupDropdown)
    // },

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

    async removeNodeFromGroup(event) {
      if (!confirm('Are you sure that you want to remove this value from the group?')) {
        return
      }

      this.loading = true
      await this.request('zigbee.mqtt.group_remove_device', {
        group: event.group,
        device: event.device,
      })

      this.loading = false
    },
  },

  created() {
    // const self = this
    // this.bus.$on('refresh', this.refresh)
    // this.bus.$on('refreshDevices', this.refreshDevices)
    // this.bus.$on('refreshGroups', this.refreshGroups)
    // this.bus.$on('openAddToGroupModal', () => {self.modal.group.visible = true})
    // this.bus.$on('openAddToGroupDropdown', this.openAddToGroupDropdown)
    // this.bus.$on('removeFromGroup', this.removeNodeFromGroup)
    //
    // registerEventHandler(() => {
    //   createNotification({
    //     text: 'WARNING: The controller is now offline',
    //     error: true,
    //   })
    // }, 'platypush.message.event.zigbee.mqtt.ZigbeeMqttOfflineEvent')
    //
    // registerEventHandler(() => {
    //   createNotification({
    //     text: 'The controller is now online',
    //     iconClass: 'fas fa-check',
    //   })
    // }, 'platypush.message.event.zigbee.mqtt.ZigbeeMqttOfflineEvent')
    //
    // registerEventHandler(() => {
    //   createNotification({
    //     text: 'Failed to remove the device',
    //     error: true,
    //   })
    // }, 'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceRemovedFailedEvent')
    //
    // registerEventHandler(() => {
    //   createNotification({
    //     text: 'Failed to add the group',
    //     error: true,
    //   })
    // }, 'platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupAddedFailedEvent')
    //
    // registerEventHandler(() => {
    //   createNotification({
    //     text: 'Failed to remove the group',
    //     error: true,
    //   })
    // }, 'platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupRemovedFailedEvent')
    //
    // registerEventHandler(() => {
    //   createNotification({
    //     text: 'Failed to remove the devices from the group',
    //     error: true,
    //   })
    // }, 'platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupRemoveAllFailedEvent')
    //
    // registerEventHandler((event) => {
    //   createNotification({
    //     text: 'Unhandled Zigbee error: ' + (event.error || '[Unknown error]'),
    //     error: true,
    //   })
    // }, 'platypush.message.event.zigbee.mqtt.ZigbeeMqttErrorEvent')
    //
    // registerEventHandler((event) => {
    //   self.updateProperties(event.device, event.properties)
    // }, 'platypush.message.event.zigbee.mqtt.ZigbeeMqttDevicePropertySetEvent')
    //
    // registerEventHandler(this.refresh,
    //     'platypush.message.event.zigbee.mqtt.ZigbeeMqttOnlineEvent',
    //     'platypush.message.event.zigbee.mqtt.ZigbeeMqttDevicePairingEvent',
    //     'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceConnectedEvent',
    //     'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceBannedEvent',
    //     'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceRemovedEvent',
    //     'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceWhitelistedEvent',
    //     'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceRenamedEvent',
    //     'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceBindEvent',
    //     'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceUnbindEvent',
    //     'platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupAddedEvent',
    //     'platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupRemovedEvent',
    //     'platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupRemoveAllEvent',
    // )
  },

  mounted() {
    this.refresh()
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
}
</style>

<template>
  <div class="item device" :class="{selected: selected}">
    <Loading v-if="loading" />

    <Modal class="groups-modal" ref="groupsModal" title="Device groups">
      <Loading v-if="loading" />

      <form class="content" @submit.prevent="manageGroups">
        <div class="groups">
          <label class="row group" v-for="(group, id) in groups" :key="id">
            <input type="checkbox" :value="id" :checked="associatedGroups.has(parseInt(group.id))">
            <span class="name" v-text="group.friendly_name?.length ? group.friendly_name : `[Group #${group.id}]`" />
          </label>
        </div>

        <div class="footer buttons">
          <button type="submit">Save</button>
        </div>
      </form>
    </Modal>

    <div class="row name header vertical-center" :class="{selected: selected}"
         v-text="device.friendly_name || device.ieee_address" @click="$emit('select')" />

    <div class="params" v-if="selected">
      <div class="row">
        <div class="param-name">Name</div>
        <div class="param-value">
          <div class="name-edit" :class="{hidden: !editName}">
            <form @submit.prevent="rename">
              <label>
                <input type="text" name="name" ref="name" :value="device.friendly_name">
              </label>

              <span class="buttons">
                <button type="button" class="btn btn-default" @click="editName = false">
                  <i class="fas fa-times"></i>
                </button>

                <button type="submit" class="btn btn-default">
                  <i class="fa fa-check"></i>
                </button>
              </span>
            </form>
          </div>

          <div class="name-edit" :class="{hidden: editName}">
            <span v-text="device.friendly_name"></span>
            <span class="buttons">
              <button type="button" class="btn btn-default" @click="editName = true">
                <i class="fa fa-edit"></i>
              </button>
            </span>
          </div>
        </div>
      </div>

      <div class="row">
        <div class="param-name">IEEE Address</div>
        <div class="param-value" v-text="device.ieee_address"></div>
      </div>

      <div class="row" v-if="device.network_address">
        <div class="param-name">Network Address</div>
        <div class="param-value" v-text="device.network_address"></div>
      </div>

      <div class="row">
        <div class="param-name">Type</div>
        <div class="param-value" v-text="device.type"></div>
      </div>

      <div class="row" v-if="device.definition?.vendor">
        <div class="param-name">Vendor</div>
        <div class="param-value">
          {{ device.definition.vendor }}
        </div>
      </div>

      <div class="row" v-if="device.definition?.model">
        <div class="param-name">Model</div>
        <div class="param-value">
          {{ device.definition.model }}
        </div>
      </div>

      <div class="row" v-if="device.model_id">
        <div class="param-name">Model ID</div>
        <div class="param-value">
          {{ device.model_id }}
        </div>
      </div>

      <div class="row" v-if="device.definition?.description">
        <div class="param-name">Description</div>
        <div class="param-value">
          {{ device.definition.description }}
        </div>
      </div>

      <div class="row" v-if="device.software_build_id">
        <div class="param-name">Software Build ID</div>
        <div class="param-value">
          {{ device.software_build_id }}
        </div>
      </div>

      <div class="row" v-if="device.definition?.date_code">
        <div class="param-name">Date Code</div>
        <div class="param-value">
          {{ device.definition.date_code }}
        </div>
      </div>

      <div class="row" v-if="device.power_source">
        <div class="param-name">Power Source</div>
        <div class="param-value">
          {{ device.power_source }}
        </div>
      </div>

      <div class="section values" v-if="Object.keys(displayedValues).length">
        <div class="header">
          <div class="title">Values</div>
        </div>

        <div class="body">
          <div class="row value" v-for="(value, property) in displayedValues" :key="property">
            <div class="param-name">
              {{ value.description }}
              <span class="text" v-if="rgbColor != null && (value.value?.x != null && value.value?.y != null) ||
                                       (value.value?.hue != null && value.value?.saturation != null)">Color</span>
              <span class="name" v-text="value.property" v-if="value.property" />
              <span class="unit" v-text="value.unit" v-if="value.unit" />
            </div>

            <div class="param-value">
              <ToggleSwitch :value="value.value_on != null ? value.value === value.value_on : !!value.value"
                            :disabled="!value.writable" v-if="value.type === 'binary'"
                            @input="setValue(value, $event)" />

              <Slider :with-label="true" :range="[value.value_min, value.value_max]" :value="value.value"
                      :disabled="!value.writable" @change="setValue(value, $event)"
                      v-else-if="value.type === 'numeric' && value.value_min != null && value.value_max != null" />

              <label v-else-if="value.type === 'numeric' && (value.value_min == null || value.value_max == null)">
                <input type="number" :with-label="true" :value="value.value" :disabled="!value.writable"
                       @change="setValue(value, $event)" />
              </label>

              <label v-else-if="value.type === 'enum'">
                <select :value="value.readable && value.value != null ? value.value : ''"
                        @change="setValue(value, $event)">
                  <option v-if="!value.readable" />
                  <option v-for="option in value.values" :key="option" :value="option" v-text="option"
                          :selected="value.readable && value.value === option" :disabled="!value.writable" />
                </select>
              </label>

              <label v-else-if="rgbColor != null && (value.value?.x != null && value.value?.y != null) ||
                                (value.value?.hue != null && value.value?.saturation != null)">
                <input type="color" @change.stop="setValue(value, $event)"
                       :value="'#' + rgbColor.map((i) => { i = Number(i).toString(16); return i.length === 1 ? '0' + i : i }).join('')" />
              </label>

              <label v-else>
                <input type="text" :disabled="!value.writable" :value="value.value" @change="setValue(value, $event)" />
              </label>
            </div>
          </div>
        </div>
      </div>

      <div class="section actions">
        <div class="header">
          <div class="title">Actions</div>
        </div>

        <div class="body">
          <div class="row" @click="$refs.groupsModal.show()">
            <div class="param-name">Manage groups</div>
            <div class="param-value">
              <i class="fa fa-network-wired" />
            </div>
          </div>

          <div class="row" @click="otaUpdatesAvailable ? installOtaUpdates() : checkOtaUpdates()">
            <div class="param-name" v-if="!otaUpdatesAvailable">Check for updates</div>
            <div class="param-name" v-else>Install updates</div>
            <div class="param-value">
              <i class="fa fa-sync-alt" />
            </div>
          </div>

          <div class="row" @click="remove(false)">
            <div class="param-name">Remove Device</div>
            <div class="param-value">
              <i class="fa fa-trash" />
            </div>
          </div>

          <div class="row error" @click="remove(true)">
            <div class="param-name">Force Remove Device</div>
            <div class="param-value">
              <i class="fa fa-trash" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import Slider from "@/components/elements/Slider";
import ToggleSwitch from "@/components/elements/ToggleSwitch";
import Utils from "@/Utils";
import {ColorConverter} from "@/components/panels/Light/color";
import Modal from "@/components/Modal";

export default {
  name: "Device",
  components: {Modal, ToggleSwitch, Slider, Loading},
  mixins: [Utils],
  emits: ['select', 'rename', 'remove', 'groups-edit'],

  props: {
    device: {
      type: Object,
      required: true,
    },

    groups: {
      type: Object,
      default: () => {},
    },

    selected: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      editName: false,
      loading: false,
      status: {},
      otaUpdatesAvailable: false,
    }
  },

  computed: {
    values() {
      if (!this.device.definition?.exposes)
        return {}

      const extractValues = (values) => {
        const extractValue = (value, root) => {
          if (!value.features) {
            if (value.property)
              root[value.property] = value

            return
          }

          if (value.property) {
            root[value.property] = root[value.property] || {}
            root = root[value.property]
          }

          for (const feature of value.features)
            extractValue(feature, root)
        }

        const ret = {}
        for (const value of values)
          extractValue(value, ret)

        return ret
      }

      return extractValues(this.device.definition.exposes)
    },

    displayedValues() {
      const ret = {}
      const mergeValues = (obj, [key, value]) => {
        if (key in this.status)
          value = {
            ...value,
            value: this.status[key]
          }

        if (value.access != null) {
          value.readable = !!(value.access & 0x1)
          value.writable = !!(value.access & 0x2)
          delete value.access
        }

        obj[key] = value
        Object.entries(value).filter((v) => v[1] instanceof Object).reduce(mergeValues, obj[key])
        return obj
      }

      Object.entries(this.values).reduce(mergeValues, ret)
      return ret
    },

    rgbColor() {
      if (!this.displayedValues.color)
        return

      const color = this.displayedValues.color?.value
      if (!color)
        return

      if (color.x != null && color.y != null) {
        const converter = new ColorConverter({
          bri: [this.displayedValues.brightness?.value_min || 0, this.displayedValues.brightness?.value_max || 255],
        })

        return converter.xyToRgb(color.x, color.y, this.displayedValues.brightness.value)
      } else
      if (color.hue != null && (color.saturation != null || color.sat != null)) {
        const satAttr = color.saturation != null ? 'saturation' : 'sat'
        const converter = new ColorConverter({
          hue: [this.displayedValues.color.hue?.value_min || 0, this.displayedValues.color.hue.value_max || 65535],
          sat: [this.displayedValues.color[satAttr]?.value_min || 0, this.displayedValues.color[satAttr].value_max || 255],
          bri: [this.displayedValues.brightness?.value_min || 0, this.displayedValues.brightness?.value_max || 255],
        })

        return converter.hslToRgb(color.hue, color[satAttr], this.displayedValues.brightness.value)
      }

      return null
    },

    associatedGroups() {
      return new Set(Object.values(this.groups)
          .filter((group) => new Set(
              (group.members || []).map((member) => member.ieee_address)).has(this.device.ieee_address))
          .map((group) => parseInt(group.id)))
    },
  },

  methods: {
    async refresh() {
      this.loading = true
      try {
        this.status = await this.request('zigbee.mqtt.device_get',
            {device: this.device.friendly_name || this.device.ieee_address})
      } finally {
        this.loading = false
      }
    },

    async rename() {
      const name = (this.$refs.name.value || '').trim()
      if (!name.length || name === this.device.friendly_name)
        return

      this.loading = true
      try {
        await this.request('zigbee.mqtt.device_rename', {
          device: this.device.friendly_name?.length ? this.device.friendly_name : this.device.ieee_address,
          name: name,
        })

        this.$emit('rename', {name: this.device.friendly_name, newName: name});
      } finally {
        this.editName = false
        this.loading = false
      }
    },

    async remove(force) {
      if (!confirm('Are you really sure that you want to remove this device from the network?'))
        return

      force = !!force
      this.loading = true
      try {
        await this.request('zigbee.mqtt.device_remove', {
          device: this.device.friendly_name?.length ? this.device.friendly_name : this.device.ieee_address,
          force: force,
        })

        this.$emit('remove', {device: this.device.friendly_name || this.device.ieee_address});
      } finally {
        this.loading = false
      }
    },

    async setValue(value, event) {
      const request = {
        device: this.device.friendly_name || this.device.ieee_address,
        property: value.property,
        value: null,
      }

      switch (value.type) {
        case 'binary':
          if (value.value_toggle) {
            request.value = value.value_toggle
          } else if (value.value_on && value.value_off) {
            request.value = value.value === value.value_on ? value.value_off : value.value_on
          } else {
            request.value = !value.value
          }
          break

        case 'numeric':
          request.value = parseFloat(event.target.value)
          break

        case 'enum':
          if (event.target.value?.length) {
            request.value = event.target.value
          }
          break

        default:
          if ((value.x != null && value.y != null) || (value.hue != null && (value.saturation != null || value.sat != null))) {
            request.property = 'color'
            const rgb = event.target.value.slice(1)
                .split(/([0-9a-fA-F]{2})/)
                .filter((_, i) => i % 2)
                .map((i) => parseInt(i, 16))

            if ((value.x != null && value.y != null)) {
              const converter = new ColorConverter({
                bri: [this.displayedValues.brightness?.value_min || 0, this.displayedValues.brightness?.value_max || 255],
              })

              const xy = converter.rgbToXY(...rgb)
              request.value = {
                color: {
                  x: xy[0],
                  y: xy[1],
                }
              }
            } else {
              const satAttr = this.displayedValues.color.saturation != null ? 'saturation' : 'sat'
              const converter = new ColorConverter({
                hue: [this.displayedValues.color.hue?.value_min || 0, this.displayedValues.color.hue.value_max || 65535],
                sat: [this.displayedValues.color[satAttr]?.value_min || 0, this.displayedValues.color[satAttr].value_max || 255],
                bri: [this.displayedValues.brightness?.value_min || 0, this.displayedValues.brightness?.value_max || 255],
              })

              const hsl = converter.rgbToHsl(...rgb)
              request.value = {
                brightness: hsl[2],
                color: {
                  hue: hsl[0],
                }
              }

              request.value.color[satAttr] = hsl[1]
            }
          }
          break
      }

      if (request.value == null)
        return

      this.loading = true
      try {
        await this.request('zigbee.mqtt.device_set', request)
        await this.refresh()
      } finally {
        this.loading = false
      }
    },

    async manageGroups(event) {
      const groups = [...event.target.querySelectorAll('input[type=checkbox]')].reduce((obj, element) => {
        const groupId = parseInt(element.value)
        if (element.checked && !this.associatedGroups.has(groupId))
          obj.add.add(groupId)
        else if (!element.checked && this.associatedGroups.has(groupId))
          obj.remove.add(groupId)

        return obj
      }, {add: new Set(), remove: new Set()})

      const editGroups = async (action) => {
        await Promise.all([...groups[action]].map(async (groupId) => {
          await this.request(`zigbee.mqtt.group_${action}_device`, {
            group: this.groups[groupId].friendly_name,
            device: this.device.friendly_name?.length ? this.device.friendly_name : this.device.ieee_address,
          })
        }))
      }

      this.loading = true
      try {
        await Promise.all(Object.keys(groups).map(editGroups))
        this.$emit('groups-edit', groups)
      } finally {
        this.loading = false
      }
    },

    async checkOtaUpdates() {
      this.loading = true
      try {
        this.otaUpdatesAvailable = (await this.request('zigbee.mqtt.device_check_ota_updates', {
          device: this.device.friendly_name?.length ? this.device.friendly_name : this.device.ieee_address,
        })).update_available

        if (this.otaUpdatesAvailable)
          this.notify({
            text: 'A firmware update is available for the device',
            image: {
              iconClass: 'fa fa-sync-alt',
            }
          })
        else
          this.notify({
            text: 'The device is up to date',
            image: {
              iconClass: 'fa fa-check',
            }
          })
      } finally {
        this.loading = false
      }
    },

    async installOtaUpdates() {
      this.loading = true
      try {
        await this.request('zigbee.mqtt.device_install_ota_updates', {
          device: this.device.friendly_name?.length ? this.device.friendly_name : this.device.ieee_address,
        })
      } finally {
        this.loading = false
      }
    },
  },

  mounted() {
    this.$watch(() => this.selected, (newValue) => {
      if (newValue)
        this.refresh()
    })

    this.$watch(() => this.status.update_available, (newValue) => {
      this.otaUpdatesAvailable = newValue
    })

    this.subscribe((event) => {
      if (event.device !== this.device.friendly_name && event.device !== this.device.ieee_address)
        return

      this.status = {...this.status, ...event.properties}
    }, `on-property-change-${this.device.ieee_address}`,
        'platypush.message.event.zigbee.mqtt.ZigbeeMqttDevicePropertySetEvent')
  },

  unmounted() {
    this.unsubscribe(`on-property-change-${this.device.ieee_address}`)
  }
}
</script>

<style lang="scss" scoped>
@import "common";

.groups-modal {
  .content {
    min-width: 20em;
    margin: -2em;
    padding: 0;
    border: none;
    box-shadow: none;
  }

  .group {
    width: 100%;
    display: flex;
    align-items: center;
    padding: .5em 1em !important;

    input[type=checkbox] {
      margin-right: 1em;
    }
  }

  .groups {
    width: 100%;
    height: calc(100% - 3.5em);
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: auto;
  }

  .footer {
    width: 100%;
    height: 3.5em;
    display: flex;
    justify-content: right;
    align-items: center;
    padding: 0;
    background: $default-bg-2;
    border-top: $default-border-2;
  }
}

@media screen and (max-width: $tablet) {
  .section.actions {
    .row {
      flex-direction: row-reverse;
      justify-content: left;

      .param-name {
        width: auto;
      }

      .param-value {
        width: 1.5em;
        margin-right: .5em;
      }
    }
  }
}
</style>

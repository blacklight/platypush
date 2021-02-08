<template>
  <div class="item device" :class="{selected: selected}">
    <Loading v-if="loading" />
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
              <span class="text" v-if="value.value?.x != null && value.value?.y != null">Color (XY coordinates)</span>
              <span class="text" v-else-if="value.value?.hue != null && value.value?.saturation != null">Color (Hue/saturation)</span>
              <span class="name" v-text="value.property" v-if="value.property" />
              <span class="unit" v-text="value.unit" v-if="value.unit" />
            </div>

            <div class="param-value">
              <ToggleSwitch :value="value.value_on != null ? value.value === value.value_on : !!value.value"
                            v-if="value.type === 'binary'" @input="setValue(value, $event)" />

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

              <label v-else-if="(value.value?.x != null && value.value?.y != null) || (value.value?.hue != null && value.value?.saturation != null)">
<!--                <input type="color" :value="rgbColor" @change.stop="onColorSelect" />-->
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
<!--          <div class="row" @click="removeDevice(false)">-->
<!--            <div class="param-name">Remove Device</div>-->
<!--            <div class="param-value">-->
<!--              <i class="fa fa-trash"></i>-->
<!--            </div>-->
<!--          </div>-->

<!--          <div class="row error" @click="removeDevice(true)">-->
<!--            <div class="param-name">Force Remove Device</div>-->
<!--            <div class="param-value">-->
<!--              <i class="fa fa-trash"></i>-->
<!--            </div>-->
<!--          </div>-->

<!--          <div class="row" @click="banDevice">-->
<!--            <div class="param-name">Ban Device</div>-->
<!--            <div class="param-value">-->
<!--              <i class="fa fa-ban"></i>-->
<!--            </div>-->
<!--          </div>-->

<!--          <div class="row" @click="whitelistDevice">-->
<!--            <div class="param-name">Whitelist Device</div>-->
<!--            <div class="param-value">-->
<!--              <i class="fa fa-list"></i>-->
<!--            </div>-->
<!--          </div>-->
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
// import {ColorConverter} from "@/components/panels/Light/color";

export default {
  name: "Device",
  components: {ToggleSwitch, Slider, Loading},
  mixins: [Utils],
  emits: ['select', 'rename'],

  props: {
    device: {
      type: Object,
      required: true,
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
  },

  created() {
    this.refresh()
    this.$watch(() => this.selected, (newValue) => {
      if (newValue)
        this.refresh()
    })
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.item {
  &.selected {
    box-shadow: $selected-item-box-shadow;
  }

  .name.header {
    padding: 1em !important;
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: .06em;

    &.selected {
      border-radius: 1.5em;
    }
    &.selected {
      background: $selected-bg;
    }
  }

  .title {
    font-size: 1.2em;
    padding-left: .5em;
  }

  &:hover {
    background: $hover-bg;

    &.selected {
      background: $selected-bg;
    }
  }

  &:not(:last-child) {
    border-bottom: $item-border;
  }

  &:first-child {
    border-radius: 1.5em 1.5em 0 0;
  }

  &:last-child {
    border-radius: 0 0 1.5em 1.5em;
  }

  .params {
    .section {
      padding: 0;
    }
  }

  .value {
    .param-name {
      display: inline-block;

      .name {
        font-family: monospace;
        font-size: .8em;
        text-transform: unset;
        padding: 0;

        &:before {
          content: '[';
        }

        &:after {
          content: ']';
        }
      }

      .unit {
        font-size: .8em;
        &:before {
          content: ' [unit: ';
        }

        &:after {
          content: ']';
        }
      }
    }

    .param-value {
      label {
        width: 90%;
      }

      input {
        width: 100%;
      }
    }
  }

  button {
    border: 0;
    background: none;
    padding: 0 .5em;

    &:hover {
      color: $default-hover-fg;
    }
  }

  .name-edit {
    width: 100%;
    display: inline-flex;
    justify-content: right;
    align-items: center;

    form {
      width: 100%;
      display: inline-flex;
      align-items:center;
      justify-content: right;
      flex-direction: row;
    }

    .buttons {
      display: inline-flex;
      justify-content: right;
      margin: 0 0 0 .5em;
    }

    form {
      background: none;
      padding: 0;
      border: none;
      box-shadow: none;
    }
  }
}
</style>

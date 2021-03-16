<template>
  <div class="section value">
    <div class="header">
      <div class="title">
        <button class="btn btn-default btn-value-name-edit" title="Edit value name" :disabled="commandRunning"
                :data-id-on-network="value.id_on_network" @click="editName">
          <i class="fa fa-edit" />
        </button>
        {{ value.label }}
      </div>
    </div>

    <div class="body">
      <div class="row">
        <div class="param-name">Value</div>
        <div class="param-value">
          <div class="value-view" v-if="value.is_read_only">
            <div class="value-data" v-text="value.data" ></div>
            <div class="unit" v-text="value.units" v-if="value.units?.length" />
          </div>

          <div class="value-edit" v-else>
            <div :class="['col-' + (value.units?.length ? '11' : '12')]">
              <div class="list" v-if="value.type === 'List'">
                <label>
                  <select @change="onValueChange">
                    <option v-for="(data, index) in value.data_items"
                            v-text="data"
                            :key="index"
                            :selected="value.data === data"
                            :value="index">
                    </option>
                  </select>
                </label>
              </div>

              <div class="numeric slider-container"
                   v-else-if="['Int', 'Long', 'Byte', 'Decimal', 'Short'].indexOf(value.type) >= 0">
                <div class="col-10">
                  <div class="row">
                    <span class="value-min" v-text="value.min" />
                    <span class="value-max" v-text="value.max" />
                  </div>
                  <div class="row">
                    <label>
                      <Slider :range="[value.min, value.max]" :value="value.data" @change="onValueChange" />
                    </label>
                  </div>
                </div>
                <div class="col-2">
                  <label>
                    <input type="text" :value="value.data" @change="onValueChange">
                  </label>
                </div>
              </div>

              <div class="boolean" v-else-if="['Bool', 'Button'].indexOf(value.type) >= 0">
                <ToggleSwitch :value="value.data" @input="onValueChange($event, !value.data)" />
              </div>

              <div class="value-data" v-else>
                <label>
                  <input type="text" :value="value.data" @change="onValueChange" />
                </label>
              </div>
            </div>

            <div class="col-1 unit" v-text="value.units" v-if="value.units?.length" />
          </div>
        </div>
      </div>

      <div class="row" v-if="sceneId != null" style="cursor: pointer"
           @click="$emit('remove-from-scene', {valueId: value.id_on_network, sceneId: sceneId})">
        <div class="param-name">Remove From Scene</div>
        <div class="param-value">
          <i class="fa fa-trash"></i>
        </div>
      </div>

      <div class="row" style="cursor: pointer" v-if="addValueToSceneItems?.length">
        <div class="param-name">Add To Scene</div>
        <div class="param-value">
          <Dropdown title="Add to scene" icon-class="fa fa-plus">
            <DropdownItem v-for="(scene, i) in addValueToSceneItems" :key="i"
                          :text="scene.label" :disabled="commandRunning"
                          @click="$emit('add-to-scene', {sceneId: scene.scene_id, valueId: value.id_on_network})" />
          </Dropdown>
        </div>
      </div>

      <div class="row" v-if="value.help?.length">
        <div class="param-name">Help</div>
        <div class="param-value" v-text="value.help"></div>
      </div>

      <div class="row">
        <div class="param-name">Value ID</div>
        <div class="param-value" v-text="value.value_id"></div>
      </div>

      <div class="row">
        <div class="param-name">ID on Network</div>
        <div class="param-value" v-text="value.id_on_network"></div>
      </div>

      <div class="row">
        <div class="param-name">Command Class</div>
        <div class="param-value" v-text="value.command_class"></div>
      </div>

      <div class="row" v-if="value.last_update">
        <div class="param-name">Last Update</div>
        <div class="param-value" v-text="value.last_update"></div>
      </div>
    </div>
  </div>
</template>

<script>
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";
import ToggleSwitch from "@/components/elements/ToggleSwitch";
import Utils from "@/Utils";
import Slider from "@/components/elements/Slider";

export default {
  name: "Value",
  components: {Slider, Dropdown, DropdownItem, ToggleSwitch},
  mixins: [Utils],
  emits: ['remove-from-scene', 'add-to-scene', 'refresh'],

  props: {
    value: {
      type: Object,
      required: true,
    },
    node: {
      type: Object,
      required: true,
    },
    selected: {
      type: Boolean,
      default: false,
    },
    sceneId: {
      type: Number,
    },
    scenes: {
      type: Object,
      default: () => { return {} },
    },
  },

  data() {
    return {
      commandRunning: false,
    }
  },

  computed: {
    addValueToSceneItems() {
      return Object.values(this.scenes || {}).filter((scene) => {
        return !(this.value.id_on_network in scene.values)
      })
    },
  },

  methods: {
    async editName() {
      const value = this.node.values[this.value.id_on_network]
      let name = prompt('New name', value.label)
      if (name?.length)
        name = name.trim()
      if (!name?.length || name === value.label)
        return

      this.commandRunning = true
      try {
        await this.request('zwave.set_value_label', {
          id_on_network: value.id_on_network,
          new_label: name,
        })
      } finally {
        this.commandRunning = false
      }

      this.$emit('refresh')
      this.notify({
        text: 'Value successfully renamed',
        image: {
          iconClass: 'fa fa-check'
        }
      })
    },

    async onValueChange(event, data) {
      const target = event.target ? event.target : event.event.target.parentElement
      const value = this.node.values[this.value.id_on_network]

      if (data === undefined)
        data = target.value != null ? target.value : event.value

      switch (value.type) {
        case 'List':
          data = value.data_items[event.target.value]
          break

        case 'Int':
        case 'Short':
        case 'Long':
        case 'Byte':
          data = parseInt(data)
          break

        case 'Button':
        case 'Bool':
          data = !!parseInt(data)
          break

        case 'Decimal':
          data = parseFloat(data)
          break
      }

      this.commandRunning = true
      try {
        this.request('zwave.set_value', {
          id_on_network: value.id_on_network,
          data: data,
        })
      } finally {
        this.commandRunning = false
      }

      this.$emit('refresh')
      this.notify({
        text: 'Value successfully modified',
        image: {
          iconClass: 'fa fa-check'
        }
      })
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.node-container {
  &:first-child {
    .item.node {
      &:hover {
        border-radius: 1.5em 1.5em 0 0;
      }
    }
  }

  &:last-child {
    .item.node {
      &:hover {
        border-radius: 0 0 1.5em 1.5em;
      }
    }
  }
}
</style>

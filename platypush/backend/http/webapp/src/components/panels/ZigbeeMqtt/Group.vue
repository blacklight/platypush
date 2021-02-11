<template>
  <div class="item group" :class="{selected: selected}">
    <Loading v-if="loading" />
    <div class="row name header vertical-center" :class="{selected: selected}"
         v-text="group.friendly_name" @click="$emit('select')" />

    <div class="params" v-if="selected">
      <div class="section devices">
        <div class="header">
          <div class="title">Devices</div>
        </div>

        <div class="body">
          <form>
            <label class="row" v-for="(device, id) in devices" :key="id">
              <input type="checkbox" :checked="members.has(device.ieee_address)" :value="device.ieee_address"
                     @change="toggleDevice(device.ieee_address)" />
              <span class="label" v-text="device.friendly_name?.length ? device.friendly_name : device.ieee_address" />
            </label>
          </form>
        </div>
      </div>

      <div class="section actions">
        <div class="header">
          <div class="title">Actions</div>
        </div>

        <div class="body">
          <div class="row" @click="rename">
            <div class="col-10">Rename Group</div>
            <div class="buttons col-2 pull-right">
              <i class="fa fa-edit"></i>
            </div>
          </div>

          <div class="row" @click="remove">
            <div class="col-10">Remove Group</div>
            <div class="buttons col-2 pull-right">
              <i class="fa fa-trash"></i>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import Utils from "@/Utils";

export default {
  name: "Group",
  emits: ['select', 'remove', 'edit'],
  mixins: [Utils],
  components: {Loading},

  props: {
    group: {
      type: Object,
      required: true,
    },

    devices: {
      type: Object,
      default: () => { return {} },
    },

    selected: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      loading: false,
      values: {},
    }
  },

  computed: {
    devicesByAddress() {
      return Object.entries(this.devices).reduce((obj, entry) => {
        const device = entry[1]
        obj[device.ieee_address] = device
        return obj
      }, {})
    },

    members() {
      return new Set((this.group.members || []).map((member) => member.ieee_address))
    },
  },

  methods: {
    async remove() {
      if (!confirm('Are you sure that you want to remove this group?'))
        return

      this.loading = true
      try {
        await this.request('zigbee.mqtt.group_remove', {name: this.group.friendly_name})
        this.$emit('remove', {name: this.group.friendly_name})
      } finally {
        this.loading = false
      }
    },

    async rename() {
      let name = prompt('New group name', this.group.friendly_name)
      if (!name?.length)
        return

      name = name.trim()
      this.loading = true

      try {
        await this.request('zigbee.mqtt.group_rename', {
          group: this.group.friendly_name || this.group.id,
          name: name,
        })

        this.$emit('rename', {name: this.group.friendly_name, newName: name})
      } finally {
        this.loading = false
      }
    },

    async toggleDevice(ieeeAddress) {
      const device = this.devicesByAddress[ieeeAddress]
      const name = device.friendly_name?.length ? device.friendly_name : ieeeAddress
      const method = this.members.has(ieeeAddress) ? 'remove' : 'add'

      this.loading = true
      try {
        await this.request(`zigbee.mqtt.group_${method}_device`, {
          group: this.group.friendly_name,
          device: name,
        })

        this.$emit('edit', {device: name, method: method})
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.section {
  padding-left: 1em !important;
}

form {
  margin: 0;
  padding: 0;
  border: none;
  box-shadow: none;

  .row {
    background: none !important;

    &:hover {
      background: $hover-bg !important;
    }

    .label {
      margin-left: .75em;
      font-weight: normal;
    }
  }
}
</style>

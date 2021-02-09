<template>
  <div class="item group" :class="{selected: selected}">
    <Loading v-if="loading" />
    <div class="row name header vertical-center" :class="{selected: selected}"
         v-text="group.friendly_name" @click="$emit('select')" />

    <div class="params" v-if="selected">
      <div class="section values">
        <div class="header">
          <div class="title">Values</div>
        </div>

        <div class="body">
<!--          <div class="row" v-for="(value, name) in properties" :key="name">-->
<!--            <div class="param-name" v-text="name"></div>-->
<!--            <div class="param-value">-->
<!--              <div v-if="name === 'state'">-->
<!--                <toggle-switch :value="value" @toggled="toggleState"></toggle-switch>-->
<!--              </div>-->
<!--              <div v-else>-->
<!--                <input type="text" :value="value" :data-name="name" @change="setValue">-->
<!--              </div>-->
<!--            </div>-->
<!--          </div>-->
        </div>
      </div>

<!--      <div class="section devices">-->
<!--        <div class="header">-->
<!--          <div class="title col-10">Devices</div>-->
<!--          <div class="buttons col-2">-->
<!--            <button class="btn btn-default" title="Add Devices" @click="bus.$emit('openAddToGroupModal')">-->
<!--              <i class="fa fa-plus"></i>-->
<!--            </button>-->
<!--          </div>-->
<!--        </div>-->

<!--        <div class="body">-->
<!--          <div class="row" v-for="device in group.devices">-->
<!--            <div class="col-10" v-text="device.friendly_name"></div>-->
<!--            <div class="buttons col-2">-->
<!--              <button class="btn btn-default" title="Remove from group" @click="removeFromGroup(device.friendly_name)">-->
<!--                <i class="fa fa-trash"></i>-->
<!--              </button>-->
<!--            </div>-->
<!--          </div>-->
<!--        </div>-->
<!--      </div>-->

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
// import ToggleSwitch from "@/components/elements/ToggleSwitch";
import Utils from "@/Utils";

export default {
  name: "Group",
  emits: ['select', 'remove'],
  mixins: [Utils],
  // components: {Loading, ToggleSwitch},
  components: {Loading},

  props: {
    group: {
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
      loading: false,
    }
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
      const name = prompt('New group name', this.group.friendly_name).trim()
      if (!name.length)
        return

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
  }
}
</script>

<style lang="scss" scoped>
@import "common";
</style>

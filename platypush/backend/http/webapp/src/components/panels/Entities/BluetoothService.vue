<template>
  <div class="entity bluetooth-service-container">
    <div class="head">
      <div class="col-1 icon">
        <EntityIcon
          :entity="value"
          :loading="loading"
          :error="error" />
      </div>

      <div class="col-9 label">
        <div class="name" v-text="value.name" />
      </div>

      <div class="col-2 connector pull-right">
        <ToggleSwitch
          :value="value.connected"
          :disabled="loading" 
          @input="connect"
          @click.stop />
      </div>
    </div>
  </div>
</template>

<script>
import ToggleSwitch from "@/components/elements/ToggleSwitch"
import EntityIcon from "./EntityIcon"
import EntityMixin from "./EntityMixin"

export default {
  name: 'BluetoothService',
  components: {ToggleSwitch, EntityIcon},
  mixins: [EntityMixin],

  methods: {
    async connect(event) {
      event.stopPropagation()
      this.$emit('loading', true)
      const method = (
        'bluetooth.' +
        (this.value.connected ? 'disconnect' : 'connect')
      )

      try {
        await this.request(method, {
          device: this.parent.address,
          service_uuid: this.uuid,
        })
      } finally {
        this.$emit('loading', false)
      }
    },

    async disconnect(event) {
      event.stopPropagation()
      this.$emit('loading', true)

      try {
        await this.request('bluetooth.disconnect', {
          device: this.parent.address,
        })
      } finally {
        this.$emit('loading', false)
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.switch-container {
  .switch {
    direction: rtl;
  }
}
</style>

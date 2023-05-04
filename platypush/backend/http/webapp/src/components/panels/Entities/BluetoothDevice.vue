<template>
  <div class="entity device-container">
    <div class="head">
      <div class="icon">
        <EntityIcon
          :entity="value"
          :loading="loading"
          :error="error" />
      </div>

      <div class="label">
        <div class="name" v-text="value.name" />
      </div>

      <div class="value-container" :class="{'with-children': value?.children_ids?.length}">
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
import EntityMixin from "./EntityMixin"
import EntityIcon from "./EntityIcon"
import ToggleSwitch from "@/components/elements/ToggleSwitch"

export default {
  name: 'BluetoothDevice',
  components: {EntityIcon, ToggleSwitch},
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
          device: this.value.address,
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

.device-container {
  display: flex;
  justify-content: center;

  .value-container {
    &:not(.with-children) {
      margin-right: 2.5em;
    }
  }
}
</style>

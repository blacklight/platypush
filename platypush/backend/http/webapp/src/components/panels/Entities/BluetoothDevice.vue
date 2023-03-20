<template>
  <div class="entity device-container">
    <div class="head">
      <div class="col-1 icon">
        <EntityIcon
          :entity="value"
          :loading="loading"
          :error="error" />
      </div>

      <div class="col-2 connector">
        <ToggleSwitch
          :value="value.connected"
          :disabled="loading" 
          @input="connect"
          @click.stop />
      </div>

      <div class="col-9 label">
        <div class="name" v-text="value.name" />
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

  .icon {
    margin-right: 1em;
  }

  .connector {
    width: 4em;
    margin: 0.25em 0 -0.25em 0.5em;
  }
}
</style>

<template>
  <div class="entity sensor-container">
    <div class="head">
      <div class="icon">
        <EntityIcon :entity="value" :loading="loading" :error="error" />
      </div>

      <div class="label">
        <div class="name" v-text="value.name" />
      </div>

      <div class="value-container" v-if="value.value != null">
        <span class="unit" v-text="value.unit" v-if="value.unit != null" />
        <span class="value" v-text="displayValue(value.value)" />
      </div>
    </div>
  </div>
</template>

<script>
import EntityIcon from "./EntityIcon"
import Sensor from "./Sensor"

export default {
  name: 'EnumSensor',
  components: {EntityIcon},
  mixins: [Sensor],

  methods: {
    displayValue(val) {
      if (this.value?.values && typeof(this.value.values) === 'object')
        return this.value.values[val] || val
      return val
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common";
</style>

<template>
  <div class="entity sensor-container">
    <div class="head">
      <div class="icon">
        <EntityIcon :entity="value" :loading="loading" :error="error" />
      </div>

      <div class="label">
        <div class="name" v-text="value.name" />
      </div>

      <div class="value-container" v-text="displayValue" />
    </div>
  </div>
</template>

<script>
import EntityMixin from "./EntityMixin"
import EntityIcon from "./EntityIcon"

export default {
  name: 'PercentSensor',
  components: {EntityIcon},
  mixins: [EntityMixin],
  computed: {
    displayValue() {
      if (this.value.value == null) {
        return null
      }

      let normValue = 100 * this.value.value
      return (
        normValue.toString() == normValue.toFixed(0)
        ? normValue.toFixed(0) : normValue.toFixed(1)
      ) + '%'
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common";
</style>

<template>
  <div class="entity sensor-container">
    <div class="head">
      <div class="col-1 icon">
        <EntityIcon
          :entity="value"
          :loading="loading"
          :error="error" />
      </div>

      <div class="col-s-8 col-m-9 label">
        <div class="name" v-text="value.name" />
      </div>

      <div class="col-s-3 col-m-2 pull-right" v-text="displayValue" />
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

.entity {
  .icon {
    margin-right: 1em;
  }
}
</style>

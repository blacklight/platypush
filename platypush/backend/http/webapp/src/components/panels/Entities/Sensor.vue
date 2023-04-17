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

      <div class="col-s-3 col-m-2 pull-right"
          v-if="computedValue != null">
        <span class="value" v-text="computedValue" />
        <span class="unit" v-text="value.unit"
          v-if="value.unit != null" />
      </div>
    </div>
  </div>
</template>

<script>
import EntityMixin from "./EntityMixin"
import EntityIcon from "./EntityIcon"

export default {
  name: 'Sensor',
  components: {EntityIcon},
  mixins: [EntityMixin],

  computed: {
    computedValue() {
      if (this.value.value != null)
        return this.value.value
      return this.value._value
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

.sensor-container {
  .head {
    .value {
      font-size: 1.1em;
      font-weight: bold;
      opacity: 0.7;
    }

    .unit {
      margin-left: 0.2em;
    }
  }
}
</style>

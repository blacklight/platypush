<template>
  <div class="entity sensor-container" :class="{hidden: value.value == null}">
    <div class="head">
      <div class="col-1 icon">
        <EntityIcon
          :icon="value.meta?.icon || {}"
          :loading="loading"
          :error="error" />
      </div>

      <div class="col-s-8 col-m-9 label">
        <div class="name" v-text="value.name" />
      </div>

      <div class="col-s-3 col-m-2 pull-right"
          v-if="value.value != null">
        <span class="unit" v-text="value.unit"
          v-if="value.unit != null" />
        <span class="value" v-text="value.value" />
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
}
</script>

<style lang="scss" scoped>
@import "common";

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

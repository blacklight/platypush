<template>
  <div class="entity sensor-container">
    <div class="head">
      <div class="icon">
        <EntityIcon :entity="value" :loading="loading" :error="error" />
      </div>

      <div class="label">
        <div class="name" v-text="value.name" />
      </div>

      <div class="value-container"
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
</style>

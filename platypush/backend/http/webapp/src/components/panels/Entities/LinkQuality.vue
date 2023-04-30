<template>
  <div class="entity link-quality-container">
    <div class="head">
      <div class="icon">
        <EntityIcon :entity="value" :loading="loading" :error="error" />
      </div>

      <div class="label">
        <div class="name" v-text="value.name" />
      </div>

      <div class="value-container">
        <span class="value"
          v-text="valuePercent + '%'"
          v-if="valuePercent != null" />
      </div>
    </div>
  </div>
</template>

<script>
import EntityMixin from "./EntityMixin"
import EntityIcon from "./EntityIcon"

export default {
  name: 'LinkQuality',
  components: {EntityIcon},
  mixins: [EntityMixin],

  computed: {
    valuePercent() {
      if (this.value?.value == null)
        return null

      const min = this.value.min || 0
      const max = this.value.max || 100
      return ((100 * this.value.value) / (max - min)).toFixed(0)
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common";
</style>

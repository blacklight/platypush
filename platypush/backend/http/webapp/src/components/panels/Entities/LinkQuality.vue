<template>
  <div class="entity link-quality-container">
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

      <div class="col-s-3 col-m-2 buttons pull-right">
        <span class="value-percent"
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

  data() {
    return {
      expanded: false,
    }
  },

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

.link-quality-container {
  .head {
    .value-percent {
      font-size: 1.1em;
      font-weight: bold;
      opacity: 0.7;
    }
  }
}
</style>

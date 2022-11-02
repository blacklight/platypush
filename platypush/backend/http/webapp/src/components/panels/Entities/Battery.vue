<template>
  <div class="entity battery-container">
    <div class="head">
      <div class="col-1 icon">
        <EntityIcon
          :icon="icon"
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

const thresholds = [
  {
    iconClass: 'full',
    color: '#157145',
    value: 0.9,
  },
  {
    iconClass: 'three-quarters',
    color: '#94C595',
    value: 0.825,
  },
  {
    iconClass: 'half',
    color: '#F0B67F',
    value: 0.625,
  },
  {
    iconClass: 'quarter',
    color: '#FE5F55',
    value: 0.375,
  },
  {
    iconClass: 'low',
    color: '#CC444B',
    value: 0.15,
  },
  {
    iconClass: 'empty',
    color: '#EC0B43',
    value: 0.05,
  },
]

export default {
  name: 'Battery',
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

    icon() {
      const icon = {...(this.value.meta?.icon || {})}
      let value = this.valuePercent
      let threshold = thresholds[0]

      if (value != null) {
        value = parseFloat(value) / 100
        for (const t of thresholds) {
          if (value > t.value)
            break
          threshold = t
        }
      }

      icon['class'] = `fas fa-battery-${threshold.iconClass}`
      icon['color'] = threshold.color
      return icon
    },
  },

  methods: {
    prevent(event) {
      event.stopPropagation()
      return false
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.battery-container {
  .head {
    .value-percent {
      font-size: 1.1em;
      font-weight: bold;
      opacity: 0.7;
    }
  }
}
</style>

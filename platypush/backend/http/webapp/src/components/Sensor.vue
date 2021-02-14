<template>
  <div class="sensor">
    <div class="label-container col-4" v-if="iconClass || name">
      <i :class="iconClass" v-if="iconClass" />
      <span v-text="name" v-else-if="name" />
    </div>

    <div class="value-container col-8">
      <span class="value" v-text="_value" />
    </div>
  </div>
</template>

<script>
export default {
  name: "Sensor",
  props: {
    // The FontAwesome icon class to be used.
    iconClass: {
      type: String,
      required: false,
    },

    // The name of the sensor metric.
    name: {
      type: String,
      required: false,
    },

    // Sensor value.
    value: {
      required: false,
    },

    // Sensor unit.
    unit: {
      type: String,
      required: false,
    },

    // Number of decimal units.
    decimals: {
      type: Number,
      required: false,
      default: 1,
    },

    // Set to true if the sensor holds a binary value.
    isBoolean: {
      type: Boolean,
      required: false,
      default: false,
    },
  },

  computed: {
    _value() {
      if (this.value == null)
        return 'N/A'

      if (this.isBoolean)
        return this.parseBoolean(this.value)

      let value = parseFloat(this.value)
      if (this.decimals != null)
        value = value.toFixed(this.decimals)
      if (this.unit)
        value = `${value}${this.unit}`

      return value
    },
  }
}
</script>

<style lang="scss" scoped>
.label-container {
  text-align: left;
}

.value-container {
  text-align: right;
}
</style>

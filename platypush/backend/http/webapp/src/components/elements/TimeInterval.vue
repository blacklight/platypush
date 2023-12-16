<template>
  <div class="time-interval-container">
    <div class="row">
      <div class="value-container">
        <input type="number" v-model="duration" :step="step" />
      </div>

      <div class="unit-container">
        <select v-model="selectedUnit">
          <option v-for="u in units" :key="u.value" :value="u.value">
            {{ u.label }}
          </option>
        </select>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  emits: ['input'],
  props: {
    // The value of the time interval, in seconds.
    value: {
      type: Number,
    },

    // The increment to use when changing the value.
    step: {
      type: Number,
      default: 1,
    },
  },

  data() {
    return {
      duration: null,
      selectedUnit: 'second',
      units: {
        'second': {
          label: 'Seconds',
          value: 'second',
          multiplier: 1,
        },

        'minute': {
          label: 'Minutes',
          value: 'minute',
          multiplier: 60,
        },

        'hour': {
          label: 'Hours',
          value: 'hour',
          multiplier: 3600,
        },

        'day': {
          label: 'Days',
          value: 'day',
          multiplier: 86400,
        },
      }
    }
  },

  computed: {
    unit() {
      return this.units[this.selectedUnit]
    },

    multiplier() {
      return this.unit.multiplier
    },

    seconds() {
      if (this.duration == null)
        return null

      return this.toSeconds(this.duration)
    },
  },

  watch: {
    seconds(value) {
      if (value === null)
        return

      this.duration = this.toUnit(value)
      this.$emit('input', value)
    },

    value(value) {
      this.duration = this.toUnit(value)
    },
  },

  methods: {
    toSeconds(value) {
      return value == null ? null : value * this.multiplier
    },

    toUnit(value) {
      return value == null ? null : value / this.multiplier
    },
  },

  mounted() {
    this.duration = this.toUnit(this.value)
  },
}
</script>

<style lang="scss" scoped>
.time-interval-container {
  display: flex;
  flex-direction: column;

  .row {
    display: flex;
    flex-direction: row;
    align-items: center;
  }

  .value-container {
    input {
      width: 7.5em;
    }
  }

  .unit-container {
    margin-left: 0.5em;
  }
}
</style>

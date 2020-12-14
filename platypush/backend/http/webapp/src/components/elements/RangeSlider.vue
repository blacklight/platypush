<template>
  <div class="range-slider">
    <label>
      <input class="slider" type="range" :value="v" :min="range[0]" :max="range[1]"
             :disabled="disabled" @input="input" @change="changed" @mouseup="mouseup" @mousedown="mousedown"
             @touchstart="mouseup" @touchend="mousedown" :ref="`input_${i}`" v-for="(v, i) in value" :key="i">
    </label>
  </div>
</template>

<script>
export default {
  name: "RangeSlider",
  emits: ['input', 'change', 'mouseup', 'mousedown'],
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },

    range: {
      type: Array,
      default: () => [0, 100],
    },

    value: {
      type: Array,
      default: () => [0, 100],
    },
  },

  methods: {
    getEvent(event) {
      return {
        ...event,
        target: {
          ...event.target,
          value: Object.values(this.$refs).map((input) => parseFloat(input.value)).sort(),
        }
      }
    },

    input(event) {
      this.$emit('input', this.getEvent(event))
    },

    changed(event) {
      this.$emit('change', this.getEvent(event))
    },

    mouseup(event) {
      this.$emit('mouseup', this.getEvent(event))
    },

    mousedown(event) {
      this.$emit('mousedown', this.getEvent(event))
    },
  },

  mounted() {
    if (this.value) {
      const self = this
      this.value.forEach((v, i) => {
        self.$refs[`input_${i}`].value = v
      })
    }
  },
}
</script>

<style lang="scss" scoped>
.range-slider {
  position: relative;
  display: flex;

  label {
    height: 2em;
  }

  .slider {
    @include appearance(none);
    @include transition(opacity .2s);
    background: none;
    width: 100%;
    height: 2em;
    position: absolute;
    left: 0;
    top: 0;
    margin: 0;
    padding: 0;
    border-radius: 1em;
    outline: none;
    pointer-events: none;
    overflow: hidden;
    z-index: 20;

    @mixin slider-thumb {
      @include appearance(none);
      position: relative;
      width: 1.5em;
      height: 1.5em;
      pointer-events: all;
      border-radius: 50%;
      border: 0;
      background: $slider-thumb-bg;
      cursor: pointer;
      z-index: 10;
      outline: 0;
    }

    &::-webkit-slider-thumb { @include slider-thumb }
    &::-moz-range-thumb { @include slider-thumb}
    &::-moz-range-track {
      @include appearance(none);
      position: relative;
      border: 0;
    }

    &::-moz-range-progress { height: 1em; }

    &:first-child {
      z-index: 21;
      &::-moz-range-progress { background: $slider-bg; }
    }

    &:last-child {
      background: $slider-bg;
      &::-moz-range-progress { background: $slider-progress-bg; }
    }

    &[disabled] {
      opacity: 0.3;
      @mixin no-thumb {
        display: none;
        width: 0;
      }

      &::-moz-range-progress { background: none; }
      &::-webkit-slider-runnable-track { background: none; }
      &::-moz-range-thumb { @include no-thumb; }
      &::-webkit-slider-thumb { @include no-thumb; }
    }
  }
}
</style>
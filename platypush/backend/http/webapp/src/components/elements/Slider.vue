<template>
  <label>
    <input class="slider" type="range" :min="range[0]" :max="range[1]" :value="value"
           @change="$emit('input', $event)" @mouseup="$emit('mouseup', $event)"
           @mousedown="$emit('mousedown', $event)">
  </label>
</template>

<script>
export default {
  name: "Slider",
  emits: ['input', 'mouseup', 'mousedown'],
  props: {
    value: {
      type: Number,
    },

    disabled: {
      type: Boolean,
      default: false,
    },

    range: {
      type: Array,
      default: () => [0, 100],
    },
  },
}
</script>

<style lang="scss" scoped>
.slider {
  @include appearance(none);
  @include transition(opacity .2s);
  width: 100%;
  height: 1em;
  border-radius: 0.33em;
  background: $slider-bg;
  outline: none;

  &::-webkit-slider-thumb {
    @include appearance(none);
    width: 1.5em;
    height: 1.5em;
    border-radius: 50%;
    border: 0;
    background: $slider-thumb-bg;
    cursor: pointer;
  }

  &::-moz-range-thumb {
    @include appearance(none);
    width: 1.5em;
    height: 1.5em;
    border-radius: 50%;
    border: 0;
    background: $slider-thumb-bg;
    cursor: pointer;
  }

  &[disabled]::-webkit-slider-thumb {
    display: none;
    width: 0;
  }

  &[disabled]::-moz-range-thumb {
    display: none;
    width: 0;
  }

  &.disabled { opacity: 0.3; }

  &::-moz-range-track {
    @include appearance(none);
  }

  &::-moz-range-progress {
    background: $slider-progress-bg;
    height: 1em;
  }

  &[disabled]::-webkit-progress-value {
    background: none;
  }

  &[disabled]::-moz-range-progress {
    background: none;
  }
}
</style>
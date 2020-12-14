<template>
  <label>
    <input class="slider" type="range" :min="range[0]" :max="range[1]" :value="value" :disabled="disabled"
           @change="$emit('input', $event)" @mouseup="$emit('mouseup', $event)" @input="$emit('input', $event)"
           @mousedown="$emit('mousedown', $event)" @touch="$emit('input', $event)"
           @touchstart="$emit('mousedown', $event)" @touchend="$emit('mouseup', $event)">
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

  @mixin slider-thumb {
    @include appearance(none);
    width: 1.5em;
    height: 1.5em;
    border-radius: 50%;
    border: 0;
    background: $slider-thumb-bg;
    cursor: pointer;
  }

  &::-webkit-slider-thumb { @include slider-thumb; }
  &::-moz-range-thumb { @include slider-thumb; }
  &::-moz-range-track { @include appearance(none); }

  &::-webkit-progress-value,
  &::-moz-range-progress {
    background: $slider-progress-bg;
    height: 1em;
  }

  &[disabled] {
    opacity: 0.3;

    &::-webkit-progress-value,
    &::-moz-range-progress {
      background: none;
    }

    &::-webkit-slider-thumb,
    &::-moz-range-thumb {
      display: none;
      width: 0;
    }
  }
}
</style>
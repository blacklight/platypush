<template>
  <label>
    <input class="slider" type="range" :min="range[0]" :max="range[1]" :value="value" :disabled="disabled"
           @change="$emit('input', $event)" @mouseup="$emit('mouseup', $event)" @input="$emit('input', $event)"
           @mousedown="$emit('mousedown', $event)" @touch="$emit('input', $event)"
           @touchstart="$emit('mousedown', $event)" @touchend="$emit('mouseup', $event)">

    <span class="label" v-if="withLabel" v-text="value" />
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

    withLabel: {
      type: Boolean,
      default: false,
    }
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
    &::-webkit-progress-value,
    &::-moz-range-progress {
      opacity: .5;
    }

    &::-webkit-slider-thumb,
    &::-moz-range-thumb {
      opacity: .4;
    }
  }
}

label {
  position: relative;
  .label {
    font-weight: normal;
    text-align: center;
  }
}
</style>

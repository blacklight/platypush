<template>
  <div class="range-wrapper">
    <input class="slider" type="range" :value="v" :min="range[0]" :max="range[1]" :step="step"
           :disabled="disabled" ref="ranges"
           @input.stop="onUpdate"
           @change.stop="onUpdate"
           @mouseup.stop="onUpdate"
           @mousedown.stop="onUpdate"
           @touchstart.stop="onUpdate"
           @touchend.stop="onUpdate"
           @keyup.stop="onUpdate"
           @keydown.stop="onUpdate"
           v-for="(v, i) in value" :key="i">
  </div>
</template>

<script>
export default {
  name: "RangeSlider",
  emits: ['input', 'change', 'mouseup', 'mousedown', 'touchstart', 'touchend', 'keyup', 'keydown'],
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },

    range: {
      type: Array,
      default: () => [0, 100],
    },

    step: {
      type: Number,
      default: 1,
    },

    value: {
      type: Array,
      default: () => [0, 100],
    },
  },

  methods: {
    onUpdate(event) {
      this.$emit(event.type, {
        ...event,
        target: {
          ...event.target,
          value: this.$refs.ranges.map((input) => parseFloat(input.value)).sort(),
        }
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.range-wrapper {
  width: 100%;
  position: relative;

  @mixin runnable-track {
    width: 100%;
    height: 0.75em;
    cursor: pointer;
    animate: 0.2s;
    background: $slider-bg;
    border-radius: 0.5em;
    box-shadow: inset 1px 0px 3px 0 $slider-track-shadow;
    border: 0;
  }

  @mixin thumb {
    width: 1.25em;
    height: 1.25em;
    background: $slider-thumb-bg;
    position: relative;
    z-index: 2;
    border-radius: 50%;
    box-shadow: 1px 0px 2px 0 $slider-thumb-shadow;
    cursor: pointer;
  }

  input[type=range] {
    width: 100%;
    position: absolute;
    left: 0;
    bottom: 0;
    outline: none;
    @include appearance(none);

    &:focus, &:hover {
      outline: none;
      border: 0;
    }

    &::-webkit-slider-runnable-track {
      @include runnable-track;
    }

    &::-moz-range-track {
      @include runnable-track;
    }

    &::-moz-range-progress {
      background: $slider-progress-bg;
    }

    &::-ms-track {
      width: 100%;
      height: 0.75em;
      cursor: pointer;
      animate: 0.2s;
      background: transparent;
      border-color: transparent;
      color: transparent;
    }

    &::-ms-fill-lower,
    &::-ms-fill-upper {
      background: $slider-progress-bg;
      border-radius: 1px;
      box-shadow: none;
      border: 0;
    }

    &::-webkit-slider-thumb {
      @include thumb;
      @include appearance(none);
      margin-top: -0.25em;
    }

    &::-moz-range-thumb {
      @include thumb;
    }

    &::-ms-thumb {
      @include thumb;
    }
  }
}
</style>


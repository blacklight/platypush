<template>
  <label class="slider-wrapper">
    <span class="range-labels" :class="{'with-label': withLabel}" v-if="withRange">
      <span class="label left" v-if="withRange" v-text="range[0]" />
      <span class="label right" v-if="withRange" v-text="range[1]" />
    </span>

    <span class="slider-container">
      <input class="slider"
             type="range"
             :class="{'with-label': withLabel}"
             :min="range[0]"
             :max="range[1]"
             :step="step"
             :disabled="disabled"
             :value="value"
             ref="range"
             @input.stop="$emit('input', $event)"
             @change.stop="$emit('change', $event)">

      <span class="label" v-if="withLabel" v-text="value" ref="label"></span>
    </span>
  </label>
</template>

<script>
export default {
  emits: ['input', 'change'],
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

    step: {
      type: Number,
      default: 1,
    },

    withLabel: {
      type: Boolean,
      default: false,
    },

    withRange: {
      type: Boolean,
      default: false,
    }
  },
}
</script>

<style lang="scss" scoped>
$label-width: 3em;
$thumb-height: 1em;
$slider-height: 0.5em;

.slider-wrapper {
  width: 100%;
  display: flex;
  position: relative;
  flex-direction: column;

  .slider-container {
    width: 100%;
    display: flex;
    position: relative;
  }

  input.slider {
    width: 100%;
    background: none;
    height: 1.5em;
    position: relative;
    border-radius: 0.5em;
    cursor: pointer;
    outline: none;
    overflow: hidden;
    transition: all ease 100ms;
    @include appearance(none);

    &:active {
      filter: brightness(80%);
      cursor: grabbing;
    }

    &:hover {
      filter: saturate(130%);
    }

    &:disabled {
      cursor: not-allowed;
      opacity: 0.5;
      filter: grayscale(1);
    }

    /* Chrome and friends */
    &::-webkit-slider-runnable-track {
      position: relative;
      border-radius: $slider-height;
      background: linear-gradient($slider-bg 0 0) scroll no-repeat center /
        100% calc(#{$slider-height} + 1px);
    }

    &::-webkit-slider-runnable-track,
    &::-webkit-slider-thumb {
      -webkit-appearance: none;
      transition: all ease 100ms;
      height: $thumb-height;
    }

    &::-webkit-slider-thumb {
      --clip-top: calc((#{$thumb-height} - #{$slider-height}) * 0.5);
      --clip-bottom: calc(#{$thumb-height} - var(--clip-top));
      --clip-further: calc(100% + 1px);

      width: $thumb-height;
      background: $slider-progress-bg;
      box-shadow: calc(-100vmax - #{$thumb-height} + 2.5px) #{$slider-height} #{$slider-height} 100vmax #{$slider-progress-bg};
      border-radius: $thumb-height;
      cursor: grab;

      &:hover {
        filter: brightness(130%) blur(1px);
        cursor: grab;
      }

      clip-path: polygon(
        100% -1px,
        #{$slider-height} -1px,
        0 var(--clip-top),
        -100vmax var(--clip-top),
        -100vmax var(--clip-bottom),
        0 var(--clip-bottom),
        #{$slider-height} 100%,
        var(--clip-further) var(--clip-further)
      );
    }

    /* Firefox */
    &::-moz-range-track {
      background: $slider-bg;
      position: relative;
      height: $slider-height;
      border-radius: 0.5em;
      box-shadow: inset 1px 0px 3px 0 $slider-track-shadow;
    }

    &::-moz-range-thumb {
      $thumb-height: 1.125em;
      width: $thumb-height;
      height: $thumb-height;
      position: relative;
      background: $slider-thumb-bg;
      border-radius: 50%;
      border: none;
      cursor: grabbing;
      transition: all ease 100ms;
      @include appearance(none);

      &:hover {
        filter: brightness(130%) blur(1px);
        cursor: grab;
      }

      &:disabled {
        background: $slider-thumb-disabled-bg;
        cursor: not-allowed;
      }
    }

    &::-moz-range-progress {
      width: 100%;
      height: $slider-height;
      cursor: pointer;
      background: $slider-progress-bg;
      border-radius: 0.5em 0 0 0.5em;
    }
  }

  .range-labels {
    width: 100%;
    display: flex;

    .left {
      text-align: left;
    }

    .right {
      @extend .pull-right;
      flex-grow: 1;
    }
  }

  .label {
    width: $label-width;
    position: relative;
    font-weight: normal;
    text-align: center;
  }

  .with-label {
    width: calc(100% - $label-width);
  }
}
</style>

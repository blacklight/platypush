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
             @input.stop="onUpdate"
             @change.stop="onUpdate">

      <div class="track" :class="{'with-label': withLabel}">
        <div class="track-inner" ref="track"></div>
      </div>
      <div class="thumb" ref="thumb"></div>
      <span class="label" v-if="withLabel" v-text="value" ref="label"></span>
    </span>
  </label>
</template>

<script>
export default {
  name: "Slider",
  emits: ['input', 'change', 'mouseup', 'mousedown', 'touchstart', 'touchend', 'keyup', 'keydown'],
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

  methods: {
    onUpdate(event) {
      this.update(event.target.value)
      this.$emit(event.type, {
        ...event,
        target: {
          ...event.target,
          value: this.$refs.range.value,
        }
      })
    },

    update(value) {
      const sliderWidth = this.$refs.range.clientWidth
      const percent = (value - this.range[0]) / (this.range[1] - this.range[0])
      const innerWidth = percent * sliderWidth
      const thumb = this.$refs.thumb

      thumb.style.left = `${innerWidth - thumb.clientWidth / 2}px`
      this.$refs.thumb.style.transform = `translate(-${percent}%, -50%)`
      this.$refs.track.style.width = `${innerWidth}px`
    },
  },

  mounted() {
    if (this.value != null)
      this.update(this.value)
    this.$watch(() => this.value, (newValue) => this.update(newValue))
  },
}
</script>

<style lang="scss" scoped>
$label-width: 3em;

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

  .slider {
    width: 100%;
    cursor: pointer;
    opacity: 0;

    &::-ms-tooltip {
      display: none;
    }
  }

  .range-labels {
    width: 100%;
    display: flex;

    &.with-label {
      width: calc(100% - $label-width);
    }

    .left {
      text-align: left;
    }

    .right {
      @extend .pull-right;
      flex-grow: 1;
    }
  }

  .track {
    width: 100%;
    height: 0.75em;
    background: $slider-bg;
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    border-radius: 0.5em;
    box-shadow: inset 1px 0px 3px 0 $slider-track-shadow;
    pointer-events: none;

    .track-inner {
      width: 0;
      height: 100%;
      background: $slider-progress-bg;
      border-radius: 0.5em 0 0 0.5em;
    }

    &.with-label {
      width: calc(100% - $label-width);
    }
  }

  .thumb {
    width: 1.25em;
    height: 1.25em;
    background: $slider-thumb-bg;
    position: absolute;
    top: 50%;
    left: 0;
    transform: translate(0%, -50%);
    border-radius: 50%;
    box-shadow: 1px 0px 2px 0 $slider-thumb-shadow;
    pointer-events: none;
  }

  .label {
    width: $label-width;
    position: relative;
    font-weight: normal;
    text-align: center;
  }
}
</style>

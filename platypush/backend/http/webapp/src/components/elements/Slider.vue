<template>
  <label class="slider-wrapper">
    <input class="slider" type="range" ref="range" :min="range[0]" :max="range[1]"
           :step="step" :disabled="disabled" :value="value"
           @input.stop="onUpdate"
           @change.stop="onUpdate"
           @mouseup.stop="onUpdate"
           @mousedown.stop="onUpdate"
           @touchstart.stop="onUpdate"
           @touchend.stop="onUpdate"
           @keyup.stop="onUpdate"
           @keydown.stop="onUpdate">

   <div class="track">
     <div class="track-inner" ref="track"></div>
   </div>
   <div class="thumb" ref="thumb"></div>
   <span class="label" v-if="withLabel" v-text="value"></span>
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
      const percent = (value * 100) / (this.range[1] - this.range[0])
      this.$refs.thumb.style.left = `${percent}%`
      this.$refs.thumb.style.transform = `translate(-${percent}%, -50%)`
      this.$refs.track.style.width = `${percent}%`
    },
  },

  mounted() {
    if (this.value != null)
      this.update(this.value)
  },
}
</script>

<style lang="scss" scoped>
.slider-wrapper {
  width: 100%;
  display: flex;
  position: relative;

  .slider {
    width: 100%;
    cursor: pointer;
    opacity: 0;

    &::-ms-tooltip {
      display: none;
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

  label {
    position: relative;
    .label {
      font-weight: normal;
      text-align: center;
    }
  }
}
</style>

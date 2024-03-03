<template>
  <div class="slider-root component-row">
    <div class="col-1 icon-container" v-if="hasIcon">
      <img class="icon" :src="iconUrl" :alt="name" v-if="iconUrl?.length">
      <i class="icon" :class="iconClass" :style="iconStyle" v-else />
    </div>
    <div :class="{'col-6': hasIcon, 'col-7': !hasIcon}" v-text="name" />
    <div class="col-5 slider-container">
      <div class="slider">
        <SliderElement :value="value" :range="[parseFloat(min), parseFloat(max)]" @change="run" />
      </div>
    </div>
  </div>
</template>

<script>
import mixins from './mixins';
import SliderElement from "@/components/elements/Slider";

/**
 * This component can be used to run action on the basis of a
 * numeric value included in a specified interval (i.e. a slider).
 */
export default {
  name: "Slider",
  components: {SliderElement},
  mixins: [mixins],
  props: {
    /**
     * Minimum value for the slider (default: 0).
     */
    min: {
      type: [String, Number],
      default: 0,
    },

    /**
     * Maximum value for the slider.
     */
    max: {
      type: [String, Number],
      required: true,
    },
  },

  methods: {
    async run(event) {
      this.value = parseFloat(event.target.value)

      if (this.handlers.beforeActions)
        await this.handlers.beforeActions(this)
      for (const action of this.actions)
        await this.request_(action)
      if (this.handlers.afterActions) {
        await this.handlers.afterActions(this)
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import "mixins";

.slider-root {
  .slider-container {
    position: relative;

    .slider {
      position: absolute;
      right: 0;
    }
  }
}
</style>

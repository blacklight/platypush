<template>
  <div class="switch component-row" @click="run">
    <div class="col-10" v-text="name" />
    <div class="col-2 toggle-container">
      <div class="toggle">
        <ToggleSwitch :value="value" @input.stop="run" />
      </div>
    </div>
  </div>
</template>

<script>
import mixins from './mixins';
import ToggleSwitch from "@/components/elements/ToggleSwitch";

/**
 * This component can be used to trigger toggle actions on
 * entities with a binary (ON/OFF) state.
 */
export default {
  name: "Switch",
  components: {ToggleSwitch},
  mixins: [mixins],
  props: {
    /**
     * Display name for this switch.
     */
    name: {
      type: String,
      default: '[Unnamed switch]',
    },
  },

  data() {
    return {
      value: undefined,
    }
  },
}
</script>

<style lang="scss" scoped>
@import "mixins";

.switch {
  .toggle-container {
    position: relative;

    .toggle {
      position: absolute;
      right: 0;
    }
  }
}
</style>

<template>
  <div class="switch component-row" @click="run">
    <div class="col-1 icon-container" v-if="hasIcon">
      <img class="icon" :src="iconUrl" :alt="name" v-if="iconUrl?.length">
      <i class="icon" :class="iconClass" :style="iconStyle" v-else />
    </div>
    <div :class="{'col-9': hasIcon, 'col-10': !hasIcon}" v-text="name" />
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

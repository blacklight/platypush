<template>
  <div class="run component-row" @click="run">
    <div class="col-1 icon-container" v-if="hasIcon">
      <img class="icon" :src="iconUrl" :alt="name" v-if="iconUrl?.length">
      <i class="icon" :class="iconClass" :style="iconStyle" v-else />
    </div>
    <div :class="{'col-11': hasIcon, 'col-12': !hasIcon}" v-text="name" />
  </div>
</template>

<script>
import mixins from './mixins';

/**
 * This component is used to run one or more actions.
 */
export default {
  name: "Run",
  mixins: [mixins],
}
</script>

<style lang="scss" scoped>
@import "mixins";
</style>

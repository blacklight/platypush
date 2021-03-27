<template>
  <div class="run component-row" @click="run">
    <div :class="{'col-10': hasIcon, 'col-12': !hasIcon}" v-text="name" />
    <div class="col-2 icon-container" v-if="hasIcon">
      <img class="icon" :src="iconUrl" :alt="name" v-if="iconUrl?.length">
      <i class="icon" :class="iconClass" :style="iconStyle" v-else />
    </div>
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
  props: {
    /**
     * Component name
     */
    name: {
      type: String,
      default: '[Unnamed action]',
    },

    /**
     * Action (FontAwesome) icon class (default: `fa fa-play`)
     */
    iconClass: {
      type: String,
    },

    /**
     * Action icon URL (default: `fa fa-play`)
     */
    iconUrl: {
      type: String,
    },

    /**
     * Action icon color override, for FontAwesome icons
     */
    iconColor: {
      type: String,
    },
  },

  computed: {
    iconStyle() {
      if (!this.iconClass?.length && this.iconColor?.length)
        return

      return {'color': this.iconColor}
    },

    hasIcon() {
      return this.iconUrl?.length || this.iconClass?.length
    },
  }
}
</script>

<style lang="scss" scoped>
@import "mixins";

.run {
  .icon-container {
    position: relative;

    .icon {
      position: absolute;
      right: 0;
    }
  }
}
</style>

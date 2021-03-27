<template>
  <div class="sensor component-row" @click="run">
    <div class="col-1 icon-container" v-if="hasIcon">
      <img class="icon" :src="iconUrl" :alt="name" v-if="iconUrl?.length">
      <i class="icon" :class="iconClass" :style="iconStyle" v-else />
    </div>
    <div :class="{'col-8': hasIcon, 'col-9': !hasIcon}" v-text="name" />
    <div class="col-3 value-container">
      <div class="value">
        {{ value }}
        <span v-if="unit" v-text="unit" />
      </div>
    </div>
  </div>
</template>

<script>
import mixins from './mixins';

/**
 * This component is used to monitor values from sensors.
 */
export default {
  name: "Sensor",
  mixins: [mixins],
  props: {
    /**
     * Optional unit used for the sensor value
     */
    unit: {
      type: String,
    },
  },

  methods: {
    async run() {
      if (this.handlers.beforeActions)
        await this.handlers.beforeActions(this)

      if (this.actions?.length)
        for (const action of this.actions)
          await this.request_(action)
      else
        await this.refresh()

      if (this.handlers.afterActions) {
        await this.handlers.afterActions(this)
      }
    },
  }
}
</script>

<style lang="scss" scoped>
@import "mixins";

.sensor {
  .value-container {
    position: relative;

    .value {
      position: absolute;
      right: 0;
      font-weight: bold;
    }
  }
}
</style>

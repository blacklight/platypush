<template>
  <div class="entity-icon-container"
      :class="{'with-color-fill': !!colorFill}"
      :style="colorFillStyle">
    <img src="@/assets/img/spinner.gif" class="loading" v-if="loading">
    <i class="fas fa-circle-exclamation error" v-else-if="error" />
    <Icon v-bind="computedIcon" v-else />
  </div>
</template>

<script>
import Icon from "@/components/elements/Icon";

export default {
  name: "EntityIcon",
  components: {Icon},
  props: {
    loading: {
      type: Boolean,
      default: false,
    },

    error: {
      type: Boolean,
      default: false,
    },

    icon: {
      type: Object,
      required: true,
    },

    hasColorFill: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      component: null,
      modalVisible: false,
    }
  },

  computed: {
    colorFill() {
      return (this.hasColorFill && this.icon.color) ? this.icon.color : null
    },

    colorFillStyle() {
      return this.colorFill && !this.error ? {'background': this.colorFill} : {}
    },

    computedIcon() {
      const icon = {...this.icon}
      if (this.colorFill)
        delete icon.color
      return icon
    },

    type() {
      let entityType = (this.entity.type || '')
      return entityType.charAt(0).toUpperCase() + entityType.slice(1)
    },
  },
}
</script>

<style lang="scss" scoped>
@import "vars";

.entity-icon-container {
  width: 1.625em;
  height: 1.5em;
  display: inline-flex;
  margin-top: 0.25em;
  margin-left: 0.25em;
  position: relative;
  text-align: center;
  justify-content: center;
  align-items: center;

  &.with-color-fill {
    border-radius: 1em;
  }

  .loading {
    position: absolute;
    bottom: 0;
    transform: translate(0%, -50%);
    width: 1em;
    height: 1em;
  }

  .error {
    color: $error-fg;
  }
}
</style>

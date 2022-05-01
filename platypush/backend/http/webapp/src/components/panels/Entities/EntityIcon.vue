<template>
  <div class="entity-icon-container">
    <img src="@/assets/img/spinner.gif" class="loading" v-if="loading">
    <i class="fas fa-circle-exclamation error" v-else-if="error" />
    <Icon v-bind="icon" v-else />
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
  },

  data() {
    return {
      component: null,
      modalVisible: false,
    }
  },

  computed: {
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
  width: 2.5em;
  height: 1.5em;
  margin-top: 0.25em;
  position: relative;
  text-align: center;

  .loading {
    position: absolute;
    bottom: 0;
    transform: translate(50%, -50%);
    width: 1em;
    height: 1em;
  }

  .error {
    color: $error-fg;
    margin-left: .5em;
  }
}
</style>

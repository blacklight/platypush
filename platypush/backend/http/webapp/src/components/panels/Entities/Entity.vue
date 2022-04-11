<template>
  <div class="row item entity">
    <div class="status-container">
      <img src="@/assets/img/spinner.gif" class="loading" v-if="loading">
      <Icon v-bind="value.meta?.icon || {}" v-else />
    </div>
    <div class="component-container">
      <component :is="component" :value="value"
        @input="$emit('input', $event)"
        @loading="$emit('loading', $event)" />
    </div>
  </div>
</template>

<script>
import { defineAsyncComponent } from 'vue'
import Utils from "@/Utils"
import Icon from "@/components/elements/Icon";

export default {
  name: "Entity",
  components: {Icon},
  mixins: [Utils],
  emits: ['input', 'loading'],
  props: {
    loading: {
      type: Boolean,
      default: false,
    },

    value: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      component: null,
    }
  },

  computed: {
    type() {
      let entityType = (this.value.type || '')
      return entityType.charAt(0).toUpperCase() + entityType.slice(1)
    },
  },

  mounted() {
    if (this.type !== 'Entity')
      this.component = defineAsyncComponent(
        () => import(`@/components/panels/Entities/${this.type}`)
      )
  },
}
</script>

<style lang="scss" scoped>
@import "vars";

.entity {
  width: 100%;
  display: table;

  .status-container {
    width: 2.5em;
    height: 1.5em;
    display: table-cell;
    vertical-align: middle;
    position: relative;

    .loading {
      position: absolute;
      bottom: 0;
      transform: translate(50%, -50%);
      width: 1em;
      height: 1em;
    }
  }

  .icon-container,
  .component-container {
    height: 100%;
    display: table-cell;
    vertical-align: middle;
  }

  .component-container {
    width: calc(100% - #{$icon-container-size});
  }
}
</style>

<template>
  <div class="row item entity">
    <Loading v-if="loading" />
    <Icon v-bind="value.meta?.icon || {}" />
    <div class="component-container">
      <component :is="component" :value="value" @input="$emit('input', $event)" />
    </div>
  </div>
</template>

<script>
import { defineAsyncComponent } from 'vue'
import Utils from "@/Utils"
import Loading from "@/components/Loading"
import Icon from "@/components/elements/Icon";

export default {
  name: "Entity",
  components: {Loading, Icon},
  mixins: [Utils],
  emits: ['input'],
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

<style lang="scss">
@import "vars";

.entity {
  width: 100%;
  display: table;

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

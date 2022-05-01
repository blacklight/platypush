<template>
  <div class="row item entity-container">
    <component :is="component"
      :value="value"
      :loading="loading"
      :error="error || value?.reachable == false"
      @input="$emit('input', $event)"
      @loading="$emit('loading', $event)"
    />
  </div>
</template>

<script>
import { defineAsyncComponent } from 'vue'
import EntityMixin from "./EntityMixin"

export default {
  name: "Entity",
  mixins: [EntityMixin],
  emits: ['input', 'loading'],

  data() {
    return {
      component: null,
    }
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
@import "common";

.entity-container {
  width: 100%;
  position: relative;
  padding: 0 !important;
}
</style>

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
    if (this.type !== 'Entity') {
      const type = this.type.split('_').map((t) =>
          t[0].toUpperCase() + t.slice(1)
      ).join('')

      this.component = defineAsyncComponent(
        () => import(`@/components/panels/Entities/${type}`)
      )
    }
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

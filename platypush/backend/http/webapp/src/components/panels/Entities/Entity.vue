<template>
  <div class="row item entity-container" :class="{blink: justUpdated}">
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
      justUpdated: false,
    }
  },

  methods: {
    valuesEqual(a, b) {
      a = {...a}
      b = {...b}
      delete a.updated_at
      delete b.updated_at
      return this.objectsEqual(a, b)
    },
  },

  mounted() {
    if (this.type !== 'Entity') {
      const type = this.type.split('_').map((t) =>
          t[0].toUpperCase() + t.slice(1)
      ).join('')

      this.$watch(
          () => this.value,
          (newValue, oldValue) => {
              if (this.valuesEqual(oldValue, newValue))
                return false

              this.justUpdated = true
              const self = this;
              setTimeout(() => self.justUpdated = false, 1000)
          }
      )

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

.blink {
  animation: blink-animation 1s steps(20, start);
}

@keyframes blink-animation {
  0% {
    background: initial
  }

  50% {
    background: $active-bg;
  }

  100% {
    background: initial
  }
}
</style>

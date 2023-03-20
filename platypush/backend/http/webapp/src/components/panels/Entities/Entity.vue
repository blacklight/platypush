<template>
  <div class="entity-container-wrapper"
      :class="{'with-children': hasChildren, collapsed: isCollapsed, hidden: !value?.name?.length}">
    <div class="row item entity-container"
        :class="{ 'with-children': hasChildren, collapsed: isCollapsed, blink: justUpdated }">
      <div class="adjuster" :class="{'col-12': !hasChildren, 'col-11': hasChildren}">
        <component
          :is="component"
          :value="value"
          :parent="parent"
          :children="computedChildren"
          :loading="loading"
          ref="instance"
          :error="error || value?.reachable == false"
          @click="onClick"
          @input="$emit('input', $event)"
          @loading="$emit('loading', $event)"
        />
      </div>

      <div class="col-1 collapse-toggler" @click.stop="toggleCollapsed" v-if="hasChildren">
        <i class="fas"
          :class="{'fa-chevron-down': isCollapsed, 'fa-chevron-up': !isCollapsed}" />
      </div>
    </div>

    <div class="children fade-in" v-if="!isCollapsed">
      <div class="child" v-for="entity in computedChildren" :key="entity.id">
        <Entity
         :value="entity"
         :parent="value"
         :loading="loading"
         :level="level + 1"
         @input="$emit('input', entity)" />
      </div>
    </div>
  </div>
</template>

<script>
import { defineAsyncComponent, shallowRef } from 'vue'
import EntityMixin from "./EntityMixin"
import { bus } from "@/bus";

export default {
  name: "Entity",
  mixins: [EntityMixin],
  emits: ['input', 'loading', 'update'],

  data() {
    return {
      component: null,
      justUpdated: false,
    }
  },

  computed: {
    computedChildren() {
      return Object.values(this.children || {}).filter((child) => child)
    },

    hasChildren() {
      return !!this.computedChildren.length
    },

    isCollapsed() {
      if (!this.hasChildren)
        return true

      return this.collapsed
    },

    instance() {
      return this.$refs.instance
    },
  },

  methods: {
    valuesEqual(a, b) {
      a = {...a}
      b = {...b}
      for (const key of ['updated_at', 'data']) {
        delete a[key]
        delete b[key]
      }

      return this.objectsEqual(a, b)
    },

    onClick(event) {
      if (
        event.target.classList.contains('label') ||
        event.target.classList.contains('head')
      ) {
        event.stopPropagation()
        this.toggleCollapsed()
      }
    },

    onEntityUpdate(entity) {
      // Check if any of the children have been updated
      const entityId = entity?.id
      const isChildUpdate = (
        entityId != null &&
        this.children &&
        entityId in this.children
      )

      if (!isChildUpdate)
        return

      this.setJustUpdated()
    },

    toggleCollapsed() {
      this.collapsed = !this.collapsed
      // Propagate the collapsed state to the wrapped component if applicable
      if (this.instance)
        this.instance.collapsed = !this.instance.collapsed
    },

    setJustUpdated() {
      this.justUpdated = true
      const self = this;
      setTimeout(() => self.justUpdated = false, 1000)
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

              this.setJustUpdated()
              this.$emit('update', {value: newValue})
          }
      )

      this.component = shallowRef(
        defineAsyncComponent(
          () => import(`@/components/panels/Entities/${type}`)
        )
      )
    }

    bus.onEntity(this.onEntityUpdate)
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.entity-container-wrapper {
  &.with-children:not(.collapsed) {
    box-shadow: 0 3px 4px 0 $default-shadow-color;
  }
}

.entity-container {
  width: 100%;
  display: flex;
  align-items: center;
  position: relative;
  padding: 0 !important;
  border-bottom: $default-border-3;

  &.with-children:not(.collapsed) {
    background: $selected-bg;
    font-weight: bold;
    box-shadow: 0 0 3px 2px $default-shadow-color;
  }

  &:hover {
    background: $hover-bg;
  }

  .collapse-toggler {
    display: flex;
    justify-content: center;
    align-items: center;
    flex: 1;
    min-height: 3em;
    margin-left: 0;
    cursor: pointer;

    &:hover {
      color: $default-hover-fg;
    }
  }

  .adjuster {
    cursor: pointer;
  }
}

:deep(.entity-container) {
  .head {
    .name {
      display: inline-flex;

      &:hover {
        color: $hover-fg;
      }
    }

    .label {
      margin-left: 0.5em;
    }

    .icon:hover {
      color: $hover-fg;
    }
  }
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

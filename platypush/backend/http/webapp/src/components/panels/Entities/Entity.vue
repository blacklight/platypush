<template>
  <div class="entity-container-wrapper"
      :class="{'with-children': hasChildren, collapsed: isCollapsed, hidden: !value?.name?.length}">
    <div class="row item entity-container"
        :class="{ 'with-children': hasChildren, collapsed: isCollapsed, blink: justUpdated }">
      <div class="adjuster" :class="{'with-children': hasChildren}">
        <component
          :is="component"
          :value="value"
          :parent="parent"
          :children="children"
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

    <div class="children fade-in" v-if="hasChildren && !isCollapsed">
      <div class="child" v-for="entity in children" :key="entity.id">
        <Entity
         :value="entity"
         :parent="value"
         :children="childrenByParentId(entity.id)"
         :loading="loading"
         :level="level + 1"
         @show-modal="$emit('show-modal', $event)"
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
  emits: ['input', 'loading', 'update', 'show-modal'],

  data() {
    return {
      component: null,
      justUpdated: false,
    }
  },

  computed: {
    hasChildren() {
      return !!Object.keys(this.children || {}).length
    },

    isCollapsed() {
      return !this.hasChildren ? true : this.collapsed
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

    childrenByParentId(parentId) {
      const parentEntity = this.allEntities?.[parentId]
      if (!parentEntity)
        return {}

      return (parentEntity.children_ids || []).reduce((obj, entityId) => {
        const entity = this.allEntities[entityId]
        if (entity && !entity.is_configuration)
          obj[entity.id] = entity
        return obj
      }, {})
    },

    onClick(event) {
      event.stopPropagation()

      if (
        event.target.classList.contains('label') ||
        event.target.classList.contains('head')
      ) {
        // When clicking on the name or icon of the entity, stop the event
        // propagation and toggle the collapsed state instead.
        this.toggleCollapsed()
      } else {
        // Otherwise, propagate the event upwards as a request to show the
        // entity details modal.
        this.$emit('show-modal', this.value.id)
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

      this.notifyUpdate()
    },

    toggleCollapsed() {
      this.collapsed = !this.collapsed
      // Propagate the collapsed state to the wrapped component if applicable
      if (this.instance)
        this.instance.collapsed = !this.instance.collapsed
    },

    notifyUpdate() {
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

              this.notifyUpdate()
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
</style>

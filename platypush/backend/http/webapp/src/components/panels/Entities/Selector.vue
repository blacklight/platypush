<template>
  <div class="entities-selectors-container">
    <div class="selector search-container col-11"
      v-if="Object.keys(entityGroups.id || {}).length">
      <input ref="search" type="text" class="search-bar"
        title="Filter by name, plugin or ID" placeholder="🔎"
        v-model="searchTerm">
    </div>

    <div class="selector actions-container col-1 pull-right">
      <Dropdown title="Actions" icon-class="fas fa-ellipsis">
        <DropdownItem  icon-class="fas fa-sync-alt" text="Refresh"
          @click="$emit('refresh')" />
        <DropdownItem  icon-class="fas fa-square-root-variable"
          text="Set Variable" @click="$emit('show-variable-modal')" />

        <Dropdown title="Group by" text="Group by"
          icon-class="fas fa-object-ungroup" ref="groupingSelector">
          <DropdownItem v-for="g in visibleGroupings" :key="g" :text="prettifyGroupingName(g)"
            :item-class="{selected: value?.grouping === g}"
            @click="onGroupingChanged(g)" />
        </Dropdown>

        <Dropdown title="Filter groups" text="Filter groups"
            :icon-class="{fas: true, 'fa-filter': true, active: hasActiveFilter}"
            ref="groupSelector" keep-open-on-item-click>
          <DropdownItem v-for="g in sortedGroups" :key="g" :text="g"
            v-bind="iconForGroup(g)" :item-class="{selected: !!selectedGroups[g]}"
            @click.stop="toggleGroup(g)" />
        </Dropdown>
      </Dropdown>
    </div>
  </div>
</template>

<script>
import Utils from '@/Utils'
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";
import meta from './meta.json'
import pluginIcons from '@/assets/icons.json'
import { bus } from "@/bus";

export default {
  name: "Selector",
  emits: ['input', 'refresh', 'show-variable-modal'],
  mixins: [Utils],
  components: {Dropdown, DropdownItem},
  props: {
    entityGroups: {
      type: Object,
      required: true,
    },

    value: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      selectedGroups: {},
      searchTerm: '',
    }
  },

  computed: {
    visibleGroupings() {
      return Object.keys(this.entityGroups).filter(
        (grouping) => grouping !== 'id'
      )
    },

    hasActiveFilter() {
      return Object.values(this.selectedGroups).filter((val) => val === false).length > 0
    },

    sortedGroups() {
      return Object.keys(this.entityGroups[this.value?.grouping] || {}).sort()
    },

    typesMeta() {
      return meta
    },

    isGroupFilterActive() {
      return Object.keys(this.selectedGroups).length !== this.sortedGroups.length
    },

    selectedEntities() {
      if (!this.searchTerm?.length)
        return this.entityGroups.id

      const searchTerm = this.searchTerm.toLowerCase().trim()
      return Object.values(this.entityGroups.id).filter((entity) => {
        if (!this.selectedGroups[entity[this.value?.grouping]])
          return false

        if (!searchTerm?.length)
          return true

        for (const attr of ['id', 'external_id', 'name', 'plugin']) {
          if (!entity[attr])
            continue

          const entityValue = entity[attr].toString().toLowerCase()
          if (entityValue.indexOf(searchTerm) >= 0)
            return true
        }

        return false
      }).reduce((obj,  entity) => {
        obj[entity.id] = entity
        return obj
      }, {})
    },
  },

  methods: {
    prettifyGroupingName(name) {
      if (!name)
        return ''

      name = this.prettify(name)
      if (name.endsWith('y'))
        name = name.slice(0, name.length-1) + 'ie'

      name += 's'
      return name
    },

    iconForGroup(group) {
      if (this.value.grouping === 'plugin' && pluginIcons[group]) {
        const icon = pluginIcons[group]
        return {
          'icon-class': icon['class']?.length || !icon.imgUrl?.length ?
              icon['class'] : 'fas fa-gears',
          'icon-url': icon.imgUrl,
        }
      }

      return {}
    },

    sync() {
      const value = {...this.value}
      value.searchTerm = this.searchTerm
      value.selectedEntities = this.selectedEntities
      value.selectedGroups = this.selectedGroups
      this.$emit('input', value)
    },

    refreshGroupFilter() {
      this.selectedGroups = Object.keys(
        this.entityGroups[this.value?.grouping] || {}
      ).reduce(
        (obj, group) => {
          obj[group] = true
          return obj
        }, {}
      )

      this.sync()
    },

    toggleGroup(group) {
      this.selectedGroups[group] = !this.selectedGroups[group]
      this.sync()
    },

    processEntityUpdate(entity) {
      const group = entity[this.value?.grouping]
      if (group && this.selectedGroups[group] == null) {
        this.selectedGroups[group] = true
      }
    },

    onGroupingChanged(grouping) {
      if (!this.entityGroups[grouping] || grouping === this.value?.grouping)
        return false

      const value = {...this.value}
      value.grouping = grouping
      this.$emit('input', value)
    },
  },

  mounted() {
    this.refreshGroupFilter()
    this.$watch(() => this.value?.grouping, () => { this.refreshGroupFilter() })
    this.$watch(() => this.searchTerm, this.sync)
    bus.onEntity(this.processEntityUpdate)
  },
}
</script>

<style lang="scss" scoped>
.entities-selectors-container {
  width: 100%;
  display: flex;
  align-items: center;

  .selector {
    height: 100%;
    display: inline-flex;
  }

  @media (max-width: 330px) {
    .search-bar {
      display: none;
    }
  }

  .search-bar {
    margin: 0.25em 0;
  }

  @include until(#{$tablet - 1 }) {
    .search-bar {
      width: 100%;
      margin-right: 2em;
    }
  }

  @include from($tablet) {
    .search-bar {
      min-width: 400px;
      margin-left: 0.5em;
    }
  }

  :deep(.dropdown-container) {
    height: 100%;
    display: flex;

    .dropdown {
      min-width: 11em;
    }

    .icon.active {
      color: $selected-fg;
    }

    button {
      height: 100%;
    }
  }
}
</style>

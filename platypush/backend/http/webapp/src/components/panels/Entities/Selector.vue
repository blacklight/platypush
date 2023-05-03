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
      const searchTerm = (this.searchTerm || '').toLowerCase()
      return Object.values(this.entityGroups.id).filter((entity) => {
        if (!this.selectedGroups[entity[this.value?.grouping]])
         return false

        if (searchTerm?.length) {
          return (
            ((entity.name || '').toLowerCase()).indexOf(searchTerm) >= 0 ||
            ((entity.plugin || '').toLowerCase()).indexOf(searchTerm) >= 0 ||
            ((entity.external_id || '').toLowerCase()).indexOf(searchTerm) >= 0 ||
            (entity.id || 0).toString() == searchTerm
          )
        }

        return true
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

    synchronizeSelectedEntities() {
      const value = {...this.value}
      value.selectedEntities = this.selectedEntities
      this.$emit('input', value)
    },

    updateSearchTerm() {
      const value = {...this.value}
      value.searchTerm = this.searchTerm
      value.selectedEntities = this.selectedEntities
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

      this.synchronizeSelectedEntities()
    },

    toggleGroup(group) {
      this.selectedGroups[group] = !this.selectedGroups[group]
      this.synchronizeSelectedEntities()
    },

    processEntityUpdate(entity) {
      const group = entity[this.value?.grouping]
      if (group && this.selectedGroups[entity[group]] == null) {
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
    this.$watch(() => this.searchTerm, this.updateSearchTerm)
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
    }
  }

  :deep(.dropdown-container) {
    height: 100%;
    display: flex;

    .dropdown {
      min-width: 10em;

      .text {
        text-align: left;
        padding-left: 0.5em;
      }
    }

    .dropdown-container {
      button {
        width: 100%;
        background: none;
        text-align: left;
        letter-spacing: 0.01em;

        .text {
          padding-left: 0.25em;
        }

        .icon.active {
          color: $selected-fg;
        }
      }
    }

    button {
      height: 100%;
      background: $default-bg-2;
      border: 0;
      padding: 0.5em;

      &:hover {
        color: $default-hover-fg;
      }
    }

    .item {
      padding: 0.75em 0.5em;
      border: 0;
      box-shadow: none;

      .col-1.icon {
        width: 1.5em;
      }

      &.selected {
        font-weight: bold;
        background: #ffffff00;
      }

      &:hover {
        background: $hover-bg;
      }
    }
  }
}
</style>

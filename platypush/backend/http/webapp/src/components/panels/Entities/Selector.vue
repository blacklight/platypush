<template>
  <div class="entities-selectors-container">
    <div class="selector">
      <Dropdown title="Group by" icon-class="fas fa-object-ungroup" ref="groupingSelector">
        <DropdownItem v-for="g in visibleGroupings" :key="g" :text="prettifyGroupingName(g)"
          :item-class="{selected: value?.grouping === g}"
          @click="onGroupingChanged(g)" />
      </Dropdown>
    </div>

    <div class="selector" :class="{active: isGroupFilterActive}" v-if="value?.grouping">
      <Dropdown title="Filter by" icon-class="fas fa-filter" ref="groupSelector"
          keep-open-on-item-click>
        <DropdownItem v-for="g in sortedGroups" :key="g" :text="g"
          v-bind="iconForGroup(g)" :item-class="{selected: !!selectedGroups[g]}"
          @click.stop="toggleGroup(g)" />
      </Dropdown>
    </div>

    <div class="selector" v-if="Object.keys(entityGroups.id || {}).length">
      <input ref="search" type="text" class="search-bar" placeholder="🔎" v-model="searchTerm">
    </div>
  </div>
</template>

<script>
import Utils from '@/Utils'
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";
import meta from './meta.json'
import pluginIcons from '@/assets/icons.json'

export default {
  name: "Selector",
  emits: ['input'],
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
      return Object.values(this.entityGroups.id).filter((entity) => {
        if (!this.selectedGroups[entity[this.value?.grouping]])
         return false

        if (this.searchTerm?.length) {
          const searchTerm = this.searchTerm.toLowerCase()
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

    refreshGroupFilter(reset) {
      if (reset)
        this.selectedGroups = Object.keys(
          this.entityGroups[this.value?.grouping] || {}
        ).reduce(
          (obj, group) => {
            obj[group] = true
            return obj
          }, {}
        )
      else {
        for (const group of Object.keys(this.entityGroups[this.value?.grouping]))
          if (this.selectedGroups[group] == null)
            this.selectedGroups[group] = true
      }

      this.synchronizeSelectedEntities()
    },

    toggleGroup(group) {
      this.selectedGroups[group] = !this.selectedGroups[group]
      this.synchronizeSelectedEntities()
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
    this.refreshGroupFilter(true)
    this.$watch(() => this.value?.grouping, () => { this.refreshGroupFilter(true) })
    this.$watch(() => this.searchTerm, this.updateSearchTerm)
    this.$watch(() => this.entityGroups, () => { this.refreshGroupFilter(false) })
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

    &.active {
      :deep(.dropdown-container) {
        button {
          color: $default-hover-fg;
        }
      }
    }
  }

  @media (max-width: 330px) {
    .search-bar {
      display: none;
    }
  }

  :deep(.dropdown-container) {
    height: 100%;
    display: flex;

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
      padding: 0.5em 4em 0.5em 0.5em;
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

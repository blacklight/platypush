<template>
  <MenuPanel>
    <li class="header">
      <i class="icon fas fa-home" />
      <span class="name">Rooms</span>
    </li>
    <li class="row group" v-for="group in groupsSorted" :key="group.id" @click="$emit('select', group.id)">
      <span class="name col-9">
        {{ group.name || `[Group #${group.id}]` }}
      </span>
      <span class="controls col-3 pull-right">
        <ToggleSwitch :value="group.state.any_on" :disabled="group.id in (loadingGroups || {})" @input="toggleGroup(group)" />
      </span>
    </li>
  </MenuPanel>
</template>

<script>
import MenuPanel from "@/components/MenuPanel";
import ToggleSwitch from "@/components/elements/ToggleSwitch";

export default {
  name: "Groups",
  components: {ToggleSwitch, MenuPanel},
  emits: ['select', 'toggle'],
  props: {
    groups: {
      type: Object,
      default: () => {},
    },

    loadingGroups: {
      type: Object,
      default: () => {},
    }
  },

  computed: {
    groupsSorted() {
      return Object.entries(this.groups)
          .sort((a, b) => a[1].name.localeCompare(b[1].name))
          .map(([id, group]) => {
            return {
              ...group,
              id: id,
            }
          })
    },
  },

  methods: {
    toggleGroup(group) {
      this.$emit('toggle', group)
    }
  }
}
</script>

<style lang="scss" scoped>
.header {
  display: flex;

  .icon {
    margin-right: 1em;
  }
}

.group {
  display: flex;
  align-items: center;
}
</style>

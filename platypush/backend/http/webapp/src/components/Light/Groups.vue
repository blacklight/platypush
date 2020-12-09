<template>
  <MenuPanel>
    <div class="panel-row header">
      <div class="col-3">
        <i class="icon fas fa-home" />
      </div>
      <div class="col-6 name">
        Rooms
      </div>
      <div class="col-3 pull-right">
        <ToggleSwitch :value="anyLightsOn" @input="$emit('toggle')" />
      </div>
    </div>

    <div class="panel-row row group" v-for="group in groupsSorted" :key="group.id" @click="$emit('select', group.id)">
      <span class="name col-9">
        {{ group.name || `[Group ${group.id}]` }}
      </span>
      <span class="controls col-3 pull-right">
        <ToggleSwitch :value="group.state.any_on" :disabled="group.id in (loadingGroups || {})"
                      @input="$emit('toggle', group)" />
      </span>
    </div>
  </MenuPanel>
</template>

<script>
import MenuPanel from "@/components/MenuPanel";
import ToggleSwitch from "@/components/elements/ToggleSwitch";
import {ColorConverter} from "@/components/panels/Light/color";

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
    },

    colorConverter: {
      type: Object,
      default: () => new ColorConverter(),
    },
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

    anyLightsOn() {
      for (const group of Object.values(this.groups))
        if (group?.state?.any_on)
          return true

      return false
    },
  },
}
</script>

<style lang="scss" scoped>
.header {
  display: flex;
  align-items: center;
  padding-top: 0.75em !important;
  padding-bottom: 0.75em !important;

  .icon {
    margin-left: 0.5em;
  }

  .name {
    text-align: center;
  }
}

.group {
  display: flex;
  align-items: center;
}
</style>

<template>
  <div class="light" :class="{expanded: !collapsed}" ref="element">
    <div class="row">
      <span class="name col-9" @click="expandToggle">
        {{ light.name || `[Light ${light.id}]` }}
      </span>
      <span class="toggle col-3 pull-right">
        <ToggleSwitch :value="light.state.on" :disabled="loading" @input="$emit('toggle', light)" />
      </span>
    </div>

    <div class="row fade-in" v-if="!collapsed">
      <Controls :light="light" :loading="loading" :color-converter="colorConverter"
                @set-light="$emit('set-light', $event)" />
    </div>
  </div>
</template>

<script>
import ToggleSwitch from "@/components/elements/ToggleSwitch";
import Controls from "@/components/Light/Controls";
import {ColorConverter} from "@/components/panels/Light/color";

export default {
  name: "Light",
  components: {Controls, ToggleSwitch},
  emits: ['toggle', 'set-light', 'collapsed', 'expanded'],
  props: {
    light: {
      type: Object,
      default: () => {},
    },

    group: {
      type: Object,
      default: () => {},
    },

    loading: {
      type: Boolean,
      default: false,
    },

    collapsed: {
      type: Boolean,
      default: true,
    },

    colorConverter: {
      type: Object,
      default: () => new ColorConverter(),
    },
  },

  methods: {
    expandToggle() {
      this.$emit(this.collapsed ? 'expanded' : 'collapsed')
    },
  },
}
</script>

<style lang="scss" scoped>
.expanded {
  .name {
    font-size: 1.25em;
  }
}
</style>

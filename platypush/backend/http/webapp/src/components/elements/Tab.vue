<template>
  <div class="tab" :class="selected ? 'selected' : ''" @click="$emit('input')">
    <span class="icon" v-if="iconClass?.length || iconUrl?.length">
      <Icon :class="iconClass" :url="iconUrl" />
    </span> &nbsp;
    <slot />
  </div>
</template>

<script>
import Icon from "@/components/elements/Icon";

export default {
  name: "Tab",
  components: {Icon},
  emits: ['input'],
  props: {
    selected: {
      type: Boolean,
      default: false,
    },

    iconClass: {
      type: String,
    },

    iconUrl: {
      type: String,
    },
  },
}
</script>

<style lang="scss" scoped>
.tab {
  height: $tab-height;
  background: $tab-bg;
  display: flex;
  padding: 1em;
  align-items: center;
  border-right: $default-border-2;
  cursor: pointer;

  @include until($tablet) {
    flex-grow: 1;
    justify-content: center;
  }

  &.selected {
    background: $selected-bg;
    font-weight: bold;
  }

  &:hover {
    background: $hover-bg;
  }

  :deep(.icon-container) {
    width: 1.5em;
  }
}
</style>

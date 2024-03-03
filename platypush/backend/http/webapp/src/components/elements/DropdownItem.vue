<template>
  <div class="row item" :class="itemClass" @click="clicked">
    <div class="col-2 icon" v-if="iconClass?.length || iconUrl?.length">
      <Icon :class="iconClass" :url="iconUrl" />
    </div>
    <div class="text" :class="{'col-10': iconClass != null}" v-text="text" />
  </div>
</template>

<script>
import Icon from "@/components/elements/Icon";
import { bus } from "@/bus";

export default {
  components: {Icon},
  props: {
    iconClass: {
      type: String,
    },

    iconUrl: {
      type: String,
    },

    text: {
      type: String,
    },

    disabled: {
      type: Boolean,
      default: false,
    },

    itemClass: {}
  },

  methods: {
    clicked() {
      if (this.disabled)
        return false

      if (!this.$parent.keepOpenOnItemClick)
        bus.emit('dropdown-close')
    }
  }
}
</script>

<style lang="scss" scoped>
.item {
  display: flex;
  flex-direction: row !important;
  min-width: 7.5em;
  padding: 0.75em 0.5em;
  cursor: pointer;
  align-items: center;
  color: $default-fg-2;
  border: 0 !important;
  cursor: pointer !important;
  box-shadow: none !important;

  &:hover {
    background: $hover-bg !important;
  }

  &.selected {
    font-weight: bold !important;
  }

  &.disabled {
    color: $dropdown-disabled-color;
    cursor: initial;
  }

  .text {
    text-align: left;
    margin-left: 0.5em;
  }

  .icon {
    width: 1.5em;
    display: inline-flex;
    align-items: center;
  }

  :deep(.icon-container) {
    width: 2em;
    display: inline-flex;
    align-items: center;

    .icon {
      margin: 0 1.5em 0 .5em;
    }
  }
}
</style>

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

export default {
  name: "DropdownItem",
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
    clicked(event) {
      if (this.disabled)
        return false

      this.$parent.$emit('click', event)
      if (!this.$parent.keepOpenOnItemClick)
        this.$parent.visible = false
    }
  }
}
</script>

<style lang="scss" scoped>
.item {
  display: flex;
  padding: .5em .25em;
  cursor: pointer;
  align-items: center;

  &:hover {
    background: $hover-bg;
  }

  &.selected {
    font-weight: bold;
  }

  &.disabled {
    color: $dropdown-disabled-color;
    cursor: initial;
  }

  .icon {
    display: inline-flex;
    align-items: center;
    max-width: 2em;
  }

  ::v-deep(.icon-container) {
    width: 2em;
    display: inline-flex;
    align-items: center;

    .icon {
      margin: 0 1.5em 0 .5em;
    }
  }
}
</style>

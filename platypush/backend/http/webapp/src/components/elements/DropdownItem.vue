<template>
  <div class="row item" @click="clicked">
    <div class="col-1 icon">
      <i :class="iconClass" v-if="iconClass" />
    </div>
    <div class="col-11 text" v-text="text" />
  </div>
</template>

<script>
export default {
  name: "DropdownItem",
  props: {
    iconClass: {
      type: String,
    },

    text: {
      type: String,
    },

    disabled: {
      type: Boolean,
      default: false,
    },
  },

  methods: {
    clicked(event) {
      this.$parent.$emit('click', event)
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

  &.disabled {
    color: $dropdown-disabled-color;
    cursor: initial;
  }

  .icon {
    margin: 0 .5rem;
  }
}
</style>

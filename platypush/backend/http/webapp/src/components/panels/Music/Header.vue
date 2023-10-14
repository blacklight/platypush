<template>
  <div class="header">
    <slot />
  </div>
</template>

<script>
export default {
  name: "Header",
}
</script>

<style lang="scss" scoped>
@import 'vars.scss';

.header {
  width: 100%;
  height: $music-header-height;
  background: $menu-panel-bg;
  padding: .5em;
  box-shadow: $border-shadow-bottom;

  :deep(.dropdown) {
    .item.active {
      color: $default-hover-fg;
    }

    .item.selected {
      font-weight: bold;
    }
  }
}
</style>

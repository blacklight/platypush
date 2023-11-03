<template>
  <div class="tabs">
    <slot />
  </div>
</template>

<script>
export default {
  name: "Tabs",
}
</script>

<style lang="scss" scoped>
.tabs {
  background: $tabs-bg;
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  margin-top: 0.2em;
  margin-bottom: 0.2em;
  box-shadow: $border-shadow-bottom;
}
</style>

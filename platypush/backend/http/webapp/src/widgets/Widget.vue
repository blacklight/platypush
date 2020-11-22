<template>
  <div :style="style" class="widget column is-full-mobile is-half-tablet is-one-quarter-desktop">
    <slot />
  </div>
</template>

<script>
export default {
  name: "Widget",
  props: ['style'],
}
</script>

<style lang="scss" scoped>
.widget {
  background: $background-color;
  border-radius: 5px;
  margin: 0 1em 1em 0;
  display: flex;
  justify-content: center;
  align-content: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 3px 3px 0 rgba(0,0,0,0.16), 0 0 0 1px rgba(0,0,0,0.08);
}

@media screen and (max-width: $tablet){
  .widget {
    height: calc(100% - 1em);
  }
}

@media screen and (min-width: $desktop){
  .widget {
    height: calc(50% - 1em);
  }
}
</style>
<template>
<div class="no-items-container">
  <div class="no-items fade-in">
    <slot />
  </div>
</div>
</template>

<script>
export default {
  name: "NoItems",
}
</script>

<style lang="scss" scoped>
.no-items-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;

  .no-items {
    min-width: 100%;
    max-width: 100%;

    @include from($tablet) {
      min-width: 80%;
    }

    @include from($desktop) {
      min-width: 50%;
      max-width: 35em;
    }

    @include from($fullhd) {
      min-width: 33%;
    }

    background: $background-color;
    margin: 1em;
    padding: 1em;
    font-size: 1.5em;
    color: $no-items-color;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 1em;
    box-shadow: $border-shadow-bottom;
  }
}
</style>

<template>
  <div class="app-container">
    <div class="btn-container">
      <RestartButton />
    </div>

    <div class="btn-container">
      <StopButton />
    </div>
  </div>
</template>

<script>
import RestartButton from "@/components/elements/RestartButton"
import StopButton from "@/components/elements/StopButton"

export default {
  name: "Application",
  components: {RestartButton, StopButton},
}
</script>

<style lang="scss" scoped>
.app-container {
  width: 100%;
  height: 100%;
  position: relative;
  margin: 0;
  background: $background-color;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;

  :deep(.btn-container) {
    margin-bottom: 1em;

    button {
      width: 15em;

      &:hover {
        border: 1px solid $default-hover-fg;
      }
    }
  }
}
</style>

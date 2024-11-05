<template>
  <div class="floating-dropdown-container">
    <FloatingButton :disabled="disabled"
                    :iconClass="iconClass"
                    :iconUrl="iconUrl"
                    :glow="glow"
                    :left="left"
                    :right="right"
                    :title="title"
                    :top="top"
                    :bottom="bottom"
                    ref="button"
                    @click.stop="toggle($event)" />

    <div class="body-container hidden" ref="dropdownContainer">
      <DropdownBody :id="id"
                    :keepOpenOnItemClick="keepOpenOnItemClick"
                    :style="style"
                    ref="dropdown"
                    @click="onClick">
        <slot />
      </DropdownBody>
    </div>
  </div>
</template>

<script>
import Dropdown from "./Dropdown";
import DropdownBody from "./DropdownBody";
import FloatingButton from "@/components/elements/FloatingButton";

export default {
  mixins: [Dropdown, FloatingButton],
  emits: ['click'],
  components: {
    DropdownBody,
    FloatingButton,
  },
}
</script>

<style lang="scss" scoped>
.floating-dropdown-container {
  .body-container {
    position: relative;
    display: inline-flex;
    flex-direction: column;

    button {
      background: none;
      border: 0;
      padding: 0.5em;

      &:hover {
        color: $default-hover-fg;
      }
    }
  }
}
</style>

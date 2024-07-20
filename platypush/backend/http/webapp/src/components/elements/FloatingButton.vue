<template>
  <div class="floating-btn" :class="className">
    <button type="button" class="btn btn-primary" :title="title" @click="$emit('click', $event)">
      <Icon :class="iconClass" :url="iconUrl" />
    </button>
  </div>
</template>

<script>
import Icon from "@/components/elements/Icon";

export default {
  name: "FloatingButton",
  components: {Icon},
  emits: ["click"],

  props: {
    iconClass: {
      type: String,
    },
    iconUrl: {
      type: String,
    },
    class: {
      type: String,
    },
    title: {
      type: String,
    },
  },

  computed: {
    className() {
      return this.class
    }
  }
}
</script>

<style lang="scss" scoped>
.floating-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  margin: auto 1em 1em auto;

  button {
    background: $tile-bg !important;
    color: $tile-fg !important;
    width: 4em;
    height: 4em;
    border-radius: 2em;
    border: none !important;
    padding: 0;
    box-shadow: $border-shadow-bottom-right;

    &:hover {
      background: $tile-hover-bg !important;
    }
  }

  :deep(button) {
    .icon-container {
      width: 4em;

      .icon {
        margin: auto;
      }
    }
  }
}
</style>

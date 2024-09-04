<template>
  <div class="floating-btn" :class="classes">
    <button type="button"
            class="btn btn-primary"
            :class="glow ? 'with-glow' : ''"
            :disabled="disabled"
            :title="title"
            @click="$emit('click', $event)">
      <Icon :class="iconClass" :url="iconUrl" />
    </button>
  </div>
</template>

<script>
import Icon from "@/components/elements/Icon";

export default {
  components: {Icon},
  emits: ["click"],

  props: {
    disabled: {
      type: Boolean,
      default: false,
    },
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
    left: {
      type: Boolean,
      default: false,
    },
    right: {
      type: Boolean,
      default: true,
    },
    top: {
      type: Boolean,
      default: false,
    },
    bottom: {
      type: Boolean,
      default: true,
    },
    glow: {
      type: Boolean,
      default: false,
    },
  },

  computed: {
    classes() {
      const classes = {}

      if (this.left) {
        classes.left = true
      } else {
        classes.right = true
      }

      if (this.top) {
        classes.top = true
      } else {
        classes.bottom = true
      }

      if (this.class?.length) {
        classes[this.class] = true
      }

      return classes
    }
  }
}
</script>

<style lang="scss" scoped>
.floating-btn {
  position: absolute;

  &.left {
    left: 0;
    margin-left: 1em;
  }

  &.right {
    right: 0;
    margin-right: 1em;
  }

  &.top {
    top: 0;
    margin-top: 1em;
  }

  &.bottom {
    bottom: 0;
    margin-bottom: 1em;
  }

  button {
    background: $tile-bg !important;
    color: $tile-fg !important;
    width: $floating-btn-size;
    height: $floating-btn-size;
    border-radius: 2em;
    border: none !important;
    padding: 0;
    box-shadow: $border-shadow-bottom-right;

    &:hover {
      background: $tile-hover-bg !important;
    }

    &:disabled,
    &[disabled] {
      background: $default-bg-7 !important;
      color: $disabled-fg !important;
      cursor: not-allowed;
    }

    &.with-glow {
      &:not(:disabled) {
        @extend .glow;
        background: $default-bg-3 !important;
        color: $ok-fg !important;
        box-shadow: 0 0 1px 1px $selected-fg !important;

        &:hover {
          box-shadow: 0 0 1px 1px $active-glow-bg-2 !important;
          color: $play-btn-fg !important;
        }
      }
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

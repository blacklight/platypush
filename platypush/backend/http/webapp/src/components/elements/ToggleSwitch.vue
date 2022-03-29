<template>
  <div class="power-switch" :class="{disabled: disabled}" @click.stop="onInput">
    <!--suppress HtmlFormInputWithoutLabel -->
    <input type="checkbox" :checked="value">
    <label>
      <!--suppress HtmlUnknownTag -->
      <div class="switch">
        <div class="dot" />
      </div>
      <span class="label">
        <slot />
      </span>
    </label>
  </div>
</template>

<script>
export default {
  name: "ToggleSwitch",
  emits: ['input'],
  props: {
    value: {
      type: Boolean,
      default: false,
    },

    disabled: {
      type: Boolean,
      default: false,
    },
  },

  methods: {
    onInput(event) {
      if (this.disabled)
        return false

      this.$emit('input', event)
    },
  },
}
</script>

<style lang="scss" scoped>
.power-switch {
  position: relative;
  transition: transform .3s;
  transform: scale(var(--scale, 1)) translateZ(0);

  &:active {
    --scale: .96;
  }

  &.disabled {
    opacity: 0.6;
  }

  input {
    display: none;
    & + label {
      border-radius: 1em;
      display: block;
      cursor: pointer;
      position: relative;
      transition: box-shadow .4s;

      &:before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        right: 0;
        bottom: 0;
        border-radius: inherit;
        background: none;
        opacity: var(--gradient, 0);
        transition: opacity .4s;
      }

      .switch {
        position: relative;
        display: inline-block;
        vertical-align: top;
        height: 1.4em;
        width: 2.5em;
        border-radius: 1em;
        background: $slider-bg;
        box-shadow: inset 1px 0px 3px 0 $slider-track-shadow;

        &:before {
          content: '';
          position: absolute;
          left: 0;
          top: 0;
          right: 0;
          bottom: 0;
          border-radius: inherit;
          background: $slider-progress-bg;
          opacity: var(--gradient, 0);
          transition: opacity .4s;
        }

        .dot {
          background: $toggle-dot-bg;
          position: absolute;
          width: 1.5em;
          height: 1.5em;
          border-radius: 50%;
          box-shadow: 1px 0px 3.5px 0 $slider-thumb-shadow;
          left: -0.25em;
          top: -0.05em;
          transform: translateX(var(--offset, 0));
          transition: transform .4s, box-shadow .4s;

          &:before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            right: 0;
            bottom: 0;
            border-radius: inherit;
            background: $toggle-selected-dot-bg;
            opacity: var(--gradient, 0);
            transition: opacity .4s;
          }
        }
      }

      span {
        line-height: 2em;
        font-size: 1.2em;
        color: var(--text, #646B8C);
        font-weight: 500;
        display: inline-block;
        vertical-align: top;
        position: relative;
        margin-left: 0.5em;
        transition: color .4s;
      }

      & + span {
        text-align: center;
        display: block;
        position: absolute;
        left: 0;
        right: 0;
        top: 100%;
        opacity: 0;
        font-size: 1em;
        font-weight: 500;
        color: $slider-bg;
        transform: translateY(0.2em);
        transition: opacity .4s, transform .4s;
      }
    }

    &:not(:checked) {
      & + label {
        pointer-events: none;
        & + span {
          opacity: 1;
          transform: translateY(0.6em);
        }
      }
    }

    &:checked {
      & + label {
        --offset: 1.5em;
        --text: $slider-progress-bg;
        --gradient: 1;
        --shadow: rgba(0, 39, 6, .1);
      }
    }
  }
}
</style>

<template>
  <div class="menu-panel">
    <ul :style="style">
      <slot />
    </ul>
  </div>
</template>

<script>
export default {
  name: "MenuPanel",
  props: {
    style: {
      type: [String, Object, Array],
    },
  },
}
</script>

<style lang="scss">
.menu-panel {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: $menu-panel-bg;
  padding-top: 2em;

  ul {
    background: $menu-panel-content-bg;
    border-radius: 15px;
    box-shadow: $plugin-panel-shadow;
    border: 0;

    li {
      display: flex;
      padding: 0.5em;
      box-shadow: $plugin-panel-entry-shadow;
      cursor: pointer;
      border: 0;
      letter-spacing: 0.05em;

      &:hover {
        background: $hover-bg;
      }

      &:first-child {
        border-radius: 15px 15px 0 0;
        box-shadow: $plugin-panel-first-entry-shadow;
      }

      &:last-child {
        border-radius: 0 0 15px 15px;
        box-shadow: $plugin-panel-last-entry-shadow;
      }

      &.header {
        background: $menu-header-bg;
        font-weight: bold;
        box-shadow: $menu-header-shadow;

        &:hover {
          background: $menu-header-bg;
        }
      }
    }
  }
}

@media screen and (max-width: $tablet) {
  .menu-panel {
    padding-top: 0;
    ul {
      min-width: 100%;
      border-radius: 0;

      li {
        &:first-child {
          border-radius: 0;
        }

        &:last-child {
          border-radius: 0;
        }
      }
    }
  }
}

@media screen and (min-width: $tablet) {
  .menu-panel {
    ul {
      min-width: 65%;
    }
  }
}

@media screen and (min-width: $desktop) {
  .menu-panel {
    ul {
      min-width: 40%;
    }
  }
}

@media screen and (min-width: $widescreen) {
  .menu-panel {
    ul {
      min-width: 30%;
    }
  }
}

@media screen and (min-width: $fullhd) {
  .menu-panel {
    ul {
      min-width: 25%;
    }
  }
}
</style>

<template>
  <div class="menu-panel">
    <div class="content">
      <slot />
    </div>
  </div>
</template>

<script>
export default {
  name: "MenuPanel",
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

  .content {
    background: $menu-panel-content-bg;
    border-radius: 15px;
    box-shadow: $plugin-panel-shadow;
    border: 0;

    .panel-row {
      display: flex;
      margin: 0 !important;
      padding: 1em;
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
    }

    .header {
      background: $menu-header-bg;
      font-weight: bold;
      box-shadow: $menu-header-shadow;

      &:hover {
        background: $menu-header-bg;
      }
    }
  }
}

@media screen and (max-width: $desktop) {
  .menu-panel {
    padding-top: 0;

    .content {
      min-width: 100%;

      .row {
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

@media screen and (min-width: $desktop) {
  .menu-panel {
    .content {
      min-width: 75%;
    }
  }
}

@media screen and (min-width: $widescreen) {
  .menu-panel {
    .content {
      min-width: 50%;
    }
  }
}

@media screen and (min-width: $fullhd) {
  .menu-panel {
    .content {
      min-width: 35%;
    }
  }
}
</style>

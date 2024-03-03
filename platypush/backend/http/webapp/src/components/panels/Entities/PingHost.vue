<template>
  <div class="entity ping-host-container">
    <div class="head">
      <div class="col-1 icon-container">
        <span class="icon" :class="iconClass" />
      </div>

      <div class="col-10 name" @click.stop="isCollapsed = !isCollapsed">
        <div class="name" v-text="value.name" />
      </div>

      <div class="col-1 collapse-toggler" @click.stop="isCollapsed = !isCollapsed">
        <i class="fas" :class="{'fa-chevron-down': isCollapsed, 'fa-chevron-up': !isCollapsed}" />
      </div>
    </div>

    <div class="body children attributes fade-in" v-if="!isCollapsed">
      <div class="child">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Host</div>
        </div>
        <div class="value">
          <div class="name" v-text="value.name" />
        </div>
      </div>

      <div class="child" v-if="value.reachable">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Ping</div>
        </div>
        <div class="value">
          <span v-text="value.avg" /> ms
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import EntityMixin from "./EntityMixin"

export default {
  mixins: [EntityMixin],

  data() {
    return {
      isCollapsed: true,
    }
  },

  computed: {
    iconClass() {
      return this.value.reachable ? "reachable" : "unreachable"
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.ping-host-container {
  .head .icon-container {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 2em;
    margin-right: 0.5em;
    padding-right: 0;

    .icon {
      width: 1.25em;
      height: 1.25em;
      border-radius: 50%;

      &.reachable {
        background-color: $ok-fg;
      }

      &.unreachable {
        background-color: $error-fg;
      }
    }
  }
}
</style>

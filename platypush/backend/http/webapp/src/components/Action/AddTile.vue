<template>
  <div class="add-tile-container">
    <Tile class="add"
          :draggable="false"
          :read-only="true"
          @click="$emit('click')">
      <div class="add-tile">
        <span class="icon">
          <i :class="icon" />
        </span>
        <span class="name">
          {{ title }}
        </span>
      </div>
    </Tile>
  </div>
</template>

<script>
import Tile from "@/components/elements/Tile"

export default {
  emits: ['click'],
  components: { Tile },

  props: {
    icon: {
      type: String,
      default: 'fas fa-plus',
    },

    title: {
      type: String,
      required: true,
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.add-tile-container {
  position: relative;
  margin: 0.5em 0;

  .icon {
    width: 1.5em;
    height: 1.5em;
    margin-right: 0.75em;
  }

  .name {
    font-style: italic;
  }
}
</style>

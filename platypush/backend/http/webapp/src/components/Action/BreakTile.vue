<template>
  <ListItem class="break-tile"
            value="break"
            :active="active"
            :read-only="readOnly"
            :spacer-bottom="spacerBottom"
            :spacer-top="spacerTop">
    <Tile :value="value"
          class="keyword"
          :draggable="false"
          :read-only="readOnly"
          :with-delete="!readOnly"
          @click.stop
          @delete="$emit('delete')">
      <div class="tile-name">
        <span class="icon">
          <i class="fas fa-hand" />
        </span>
        <span class="name">
          <span class="keyword">break</span>
        </span>
      </div>
    </Tile>
  </ListItem>
</template>

<script>
import ListItem from "./ListItem"
import Tile from "@/components/elements/Tile"

export default {
  emits: ['delete'],

  components: {
    ListItem,
    Tile,
  },

  props: {
    value: {
      type: String,
      default: 'break',
    },

    active: {
      type: Boolean,
      default: false,
    },

    readOnly: {
      type: Boolean,
      default: false,
    },

    spacerBottom: {
      type: Boolean,
      default: true,
    },

    spacerTop: {
      type: Boolean,
      default: true,
    },
  },
}
</script>

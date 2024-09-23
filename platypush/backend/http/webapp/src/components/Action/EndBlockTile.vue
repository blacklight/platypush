<template>
  <ListItem class="end-block-container"
            :active="active"
            :value="{}"
            :read-only="false"
            :spacer-bottom="spacerBottom"
            :spacer-top="spacerTop"
            @dragenter="$emit('dragenter', $event)"
            @dragleave="$emit('dragleave', $event)"
            @dragover="$emit('dragover', $event)"
            @drop="$emit('drop', $event)">
    <Tile class="keyword" :draggable="false" :read-only="true">
      <div class="tile-name">
        <span class="icon">
          <i :class="icon" />
        </span>
        <span class="name">
          <span class="keyword" v-text="value" />
        </span>
      </div>
    </Tile>
  </ListItem>
</template>

<script>
import ListItem from "./ListItem"
import Mixin from "./Mixin"
import Tile from "@/components/elements/Tile"

export default {
  mixins: [Mixin],
  components: {
    ListItem,
    Tile,
  },

  props: {
    value: {
      type: String,
      required: true,
    },

    icon: {
      type: String,
      required: true,
    },

    active: {
      type: Boolean,
      default: false,
    },

    spacerTop: {
      type: Boolean,
      default: false,
    },

    spacerBottom: {
      type: Boolean,
      default: false,
    },
  },
}
</script>

<template>
  <div class="volume-slider-container">
    <div class="col-1">
      <button
        :disabled="status.mute == null"
        :title="status.mute ? 'Muted' : 'Unmuted'"
        @click="$emit(status.mute ? 'unmute' : 'mute')">
        <i class="icon fa fa-volume-xmark" v-if="status.mute" />
        <i class="icon fa fa-volume-up" v-else />
      </button>
    </div>

    <div class="col-11 volume-slider">
      <Slider :value="status.volume" :range="volumeRange" :disabled="status.volume == null"
              @input="$emit('set-volume', $event.target.value)" />
    </div>
  </div>
</template>

<script>
import Slider from "@/components/elements/Slider";

export default {
  components: {Slider},
  emits: ['set-volume', 'mute', 'unmute'],

  props: {
    // Volume range
    volumeRange: {
      type: Array,
      default: () => [0, 100],
    },

    // Current player status
    status: {
      type: Object,
      default: () => ({}),
    },
  },
}
</script>

<style lang="scss" scoped>
@import 'vars.scss';

.volume-slider-container {
  min-width: 15em;
  max-width: 25em;
  display: inline-flex;
  align-items: center;
  flex: 1;

  .volume-slider {
    margin: 0;
    padding: 0 .5em 0 1em;
    flex: 1;
  }

  button {
    margin: 0;
    padding: 0;
    background: transparent;
    border: none;

    &:disabled {
      cursor: default;
    }

    &:not(:disabled):hover {
      color: $default-hover-fg;
    }
  }
}
</style>

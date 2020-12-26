<template>
  <div class="media-container">
    <div class="view-container">
      <slot />
    </div>
    <div class="controls-container">
      <Controls :status="status" :track="track" @play="$emit('play', $event)" @pause="$emit('pause', $event)"
                @stop="$emit('stop')" @previous="$emit('previous')" @next="$emit('next')" @seek="$emit('seek', $event)"
                @set-volume="$emit('set-volume', $event)" @consume="$emit('consume', $event)"
                @repeat="$emit('repeat', $event)" @random="$emit('random', $event)" />
    </div>
  </div>
</template>

<script>
import Controls from "@/components/Media/Controls";

export default {
  name: "View",
  components: {Controls},
  emits: ['play', 'pause', 'stop', 'next', 'previous', 'set-volume', 'seek', 'consume', 'random', 'repeat'],
  props: {
    pluginName: {
      type: String,
      required: true,
    },

    status: {
      type: Object,
      default: () => {},
    },

    track: {
      type: Object,
    },
  },
}
</script>

<style lang="scss" scoped>
@import 'vars.scss';

.media-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;

  .view-container {
    height: calc(100% - #{$media-ctrl-panel-height});
    overflow: auto;
  }

  .controls-container {
    width: 100%;
    position: absolute;
    bottom: 0;
    border-top: $default-border-2;
    background: $default-bg-2;
    box-shadow: $border-shadow-top;
  }
}
</style>

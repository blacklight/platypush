<template>
  <div class="media-container">
    <div class="view-container">
      <slot />
    </div>
    <div class="controls-container">
      <Controls :buttons="buttons"
                :image="image"
                :status="status"
                :track="track"
                @consume="$emit('consume', $event)"
                @info="$emit('info', $event)"
                @mute="$emit('mute')"
                @next="$emit('next')"
                @pause="$emit('pause', $event)"
                @play="$emit('play', $event)"
                @previous="$emit('previous')"
                @random="$emit('random', $event)"
                @repeat="$emit('repeat', $event)"
                @search="$emit('search', $event)"
                @seek="$emit('seek', $event)"
                @set-volume="$emit('set-volume', $event)"
                @stop="$emit('stop')"
                @unmute="$emit('unmute')" />
    </div>
  </div>
</template>

<script>
import Controls from "@/components/Media/Controls";

export default {
  name: "View",
  components: {Controls},
  emits: [
    'consume',
    'info',
    'mute',
    'next',
    'pause',
    'play',
    'previous',
    'random',
    'repeat',
    'search',
    'seek',
    'set-volume',
    'stop',
    'unmute',
  ],

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

    image: {
      type: String,
      default: null,
    },

    buttons: {
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
    height: 100%;
  }

  .controls-container {
    width: 100%;
    position: absolute;
    bottom: 0;
    border-top: $default-border-2;
    background: $default-bg-2;
    box-shadow: $border-shadow-top;
    z-index: 100;
  }
}
</style>

<template>
  <div class="progress-bar-container">
    <div class="col-s-2 col-m-1 time">
        <span class="elapsed-time"
              v-text="elapsed != null && (status.state === 'play' || status.state === 'pause') ? convertTime(elapsed) : '-:--'"></span>
    </div>
    <div class="col-s-8 col-m-10 time-bar">
      <Slider :value="elapsed" :range="[0, duration]" :disabled="!duration || status.state === 'stop'"
              @change="$emit('seek', $event.target.value)" />
    </div>
    <div class="col-s-2 col-m-1 time">
        <span class="total-time"
              v-text="duration && status.state !== 'stop' ? convertTime(duration) : '-:--'"></span>
    </div>
  </div>
</template>

<script>
import MediaUtils from "@/components/Media/Utils";
import Slider from "@/components/elements/Slider";

export default {
  components: {Slider},
  emits: ['seek'],
  mixins: [MediaUtils],

  props: {
    elapsed: {
      type: Number,
    },

    duration: {
      type: Number,
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
$time-width: 2.5em;

.progress-bar-container {
  width: 100%;
  display: flex;
  align-items: center;

  .time {
    width: $time-width;
    font-size: .7em;
    position: relative;
    margin-left: 0;
  }

  .elapsed-time {
    text-align: right;
    float: right;
  }

  .time-bar {
    width: calc(100% - #{$time-width * 2} - 2em);
    flex-grow: 1;
    margin: 0 .5em;
  }
}
</style>

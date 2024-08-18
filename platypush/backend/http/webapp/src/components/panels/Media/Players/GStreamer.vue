<template>
  <div />
</template>

<script>
import Mixin from "@/components/panels/Media/Players/Mixin";

export default {
  mixins: [Mixin],
  data() {
    return {
      iconClass: 'fa fa-tv',
      name: 'GStreamer',
      pluginName: 'media.gstreamer',
    }
  },
}
</script>

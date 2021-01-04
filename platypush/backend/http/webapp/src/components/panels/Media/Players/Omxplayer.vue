<template>
  <div />
</template>

<script>
import Mixin from "@/components/panels/Media/Players/Mixin";

export default {
  name: "Omxplayer",
  mixins: [Mixin],
  data() {
    return {
      iconClass: 'fa fa-tv',
      name: 'OMXPlayer',
      pluginName: 'media.omxplayer',
    }
  },
}
</script>

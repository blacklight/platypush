<template>
  <div />
</template>

<script>
import Mixin from "@/components/panels/Media/Players/Mixin";

export default {
  name: "Mplayer",
  mixins: [Mixin],
  data() {
    return {
      iconClass: 'fa fa-tv',
      name: 'MPlayer',
      pluginName: 'media.mplayer',
    }
  },
}
</script>

<template>
  <div />
</template>

<script>
import Mixin from "@/components/panels/Media/Players/Mixin";

export default {
  name: "Mpv",
  mixins: [Mixin],
  data() {
    return {
      iconClass: 'fa fa-tv',
      name: 'mpv',
      pluginName: 'media.mpv',
    }
  },
}
</script>

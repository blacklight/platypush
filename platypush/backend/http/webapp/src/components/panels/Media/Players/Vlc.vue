<template>
  <div />
</template>

<script>
import Mixin from "@/components/panels/Media/Players/Mixin";

export default {
  name: "Vlc",
  mixins: [Mixin],
  data() {
    return {
      iconClass: 'fa fa-tv',
      name: 'VLC',
      pluginName: 'media.vlc',
    }
  },
}
</script>

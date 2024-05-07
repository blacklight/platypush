<template>
  <MusicPlugin plugin-name="music.mopidy" :fetch-status-on-update="false" />
</template>

<script>
import MusicPlugin from "@/components/panels/Music/Common"

export default {
  components: {MusicPlugin},
}
</script>

<template>
  <div class="media-file-browser">
    <Loading v-if="loading" />
    <Browser :is-media="true"
       :filter="filter"
       :has-back="true"
       @back="$emit('back')"
       @path-change="$emit('path-change', $event)"
       @play="$emit('play', $event)"
       v-else />
  </div>
</template>

<script>
import Browser from "@/components/File/Browser";
import Loading from "@/components/Loading";
import MediaProvider from "./Mixin";

export default {
  mixins: [MediaProvider],
  components: {
    Browser,
    Loading,
  },
}
</script>

<style lang="scss" scoped>
.media-file-browser {
  height: 100%;
}
</style>

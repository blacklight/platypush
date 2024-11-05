<template>
  <div class="media-file-browser">
    <Loading v-if="isLoading" />
    <Browser :is-media="true"
       :filter="filter"
       :has-back="true"
       :homepage="mediaDirs"
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

  data() {
    return {
      loading_: false,
      mediaDirs: {},
    };
  },

  computed: {
    isLoading() {
      return this.loading_ || this.loading
    },
  },

  methods: {
    async refresh() {
      this.loading_ = true

      try {
        this.mediaDirs = await this.request(`${this.mediaPlugin}.get_media_dirs`)
      } finally {
        this.loading_ = false
      }
    },
  },

  async mounted() {
    const urlPath = this.getUrlArgs().path
    if (urlPath) {
      await this.$emit('path-change', urlPath)
    }

    await this.refresh()
  },
}
</script>

<style lang="scss" scoped>
.media-file-browser {
  height: 100%;
}
</style>

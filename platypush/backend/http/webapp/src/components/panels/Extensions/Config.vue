<template>
  <div class="config-container" ref="root">
    <CopyButton :text="extension.config_snippet" />
    <pre><code class="config-snippet" v-html="highlightedConfigSnippet" /></pre>
  </div>
</template>

<script>
import 'highlight.js/lib/common'
import 'highlight.js/styles/stackoverflow-dark.min.css'
import hljs from "highlight.js"
import CopyButton from "@/components/elements/CopyButton"
import Utils from "@/Utils";

export default {
  name: "Extension",
  mixins: [Utils],
  components: {
    CopyButton,
  },
  props: {
    extension: {
      type: Object,
      required: true,
    },
  },

  computed: {
    highlightedConfigSnippet() {
      return hljs.highlight(
        'yaml',
        this.extension.config_snippet,
      ).value.trim()
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common.scss";

.config-container {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
}
</style>

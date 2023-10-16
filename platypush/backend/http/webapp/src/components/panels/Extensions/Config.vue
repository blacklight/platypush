<template>
  <div class="config-container" ref="root">
    <button class="copy-button"
            ref="copyButton"
            title="Copy to clipboard"
            :data-clipboard-text="extension.config_snippet"
            @click="copyToClipboard(extension.config_snippet)">
      <i class="fas fa-clipboard" />
    </button>
    <pre><code class="config-snippet" v-html="highlightedConfigSnippet" /></pre>
  </div>
</template>

<script>
import 'highlight.js/lib/common'
import 'highlight.js/styles/stackoverflow-dark.css'
import hljs from "highlight.js"
import Utils from "@/Utils";

export default {
  name: "Extension",
  mixins: [Utils],
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
.config-container {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;

  .copy-button {
    position: absolute;
    top: 0;
    right: 0;
    background: none;
    color: $code-dark-fg;
    border: none;
    padding: 0.5em;
    font-size: 1.5em;
    cursor: pointer;
  }

  pre {
    width: 100%;
    margin: 0;
    background: $code-dark-bg;
    padding: 0.5em;
  }
}
</style>

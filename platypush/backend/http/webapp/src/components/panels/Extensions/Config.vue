<template>
  <div class="config-container current"
       v-if="highlightedCurrentConfig">
    <CopyButton :text="curYamlConfig" />
    <pre><code class="config-snippet" v-html="highlightedCurrentConfig" /></pre>
  </div>

  <div class="config-container snippet" :class="{'fullscreen': !highlightedCurrentConfig}">
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

    config: {
      type: Object,
    },

    configFile: {
      type: String,
    },
  },

  data() {
    return {
      curYamlConfig: null,
    }
  },

  computed: {
    highlightedConfigSnippet() {
      return hljs.highlight(
        `# Configuration template. You can add it to ${this.configFile}\n` +
        this.extension.config_snippet,
        {language: 'yaml'}
      ).value.trim()
    },

    highlightedCurrentConfig() {
      if (!this.curYamlConfig) {
        return null
      }

      return hljs.highlight(
        'yaml',
        '# Currently loaded configuration\n' +
        this.curYamlConfig
      ).value.trim()
    },
  },

  methods: {
    async loadCurrentConfig() {
      if (!this.config) {
        this.curYamlConfig = null
        return
      }

      this.curYamlConfig = await this.request(
        'utils.to_yaml', {
          obj: {
            [this.extension.name]: this.config,
          }
        }
      )
    },
  },

  mounted() {
    this.loadCurrentConfig()
    this.$watch('config', this.loadCurrentConfig)
  },
}
</script>

<style lang="scss" scoped>
@import "common.scss";

.config-container {
  width: 100%;
  max-height: 100%;
  position: relative;
  display: flex;
  flex-grow: 1;
  overflow: auto;

  pre {
    border-radius: 1em;
  }

  &.current {
    height: 34%;
    margin-bottom: 1.5em;
  }

  &.snippet {
    height: 66%;
  }

  &.fullscreen {
    height: 100%;

    pre {
      border-radius: 0;
    }
  }
}
</style>

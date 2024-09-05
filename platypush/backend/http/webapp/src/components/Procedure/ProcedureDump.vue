<template>
  <div class="procedure-dump">
    <Loading v-if="loading" />

    <div class="dump-container" v-else>
      <CopyButton :text="yaml?.trim()" />
      <pre><code v-html="highlightedYAML" /></pre>
    </div>
  </div>
</template>

<script>
import 'highlight.js/lib/common'
import 'highlight.js/styles/stackoverflow-dark.min.css'
import hljs from "highlight.js"

import CopyButton from "@/components/elements/CopyButton"
import Loading from "@/components/Loading";
import Utils from "@/Utils"

export default {
  mixins: [Utils],
  components: {
    CopyButton,
    Loading
  },

  props: {
    procedure: {
      type: Object,
      required: true
    }
  },

  data() {
    return {
      loading: false,
      yaml: null,
    }
  },

  computed: {
    highlightedYAML() {
      return hljs.highlight(
        '# You can copy this code in a YAML configuration file\n' +
        '# if you prefer to store this procedure in a file.\n' +
        this.yaml || '',
        {language: 'yaml'}
      ).value
    },
  },

  methods: {
    async refresh() {
      this.loading = true
      try {
        this.yaml = await this.request('procedures.to_yaml', {procedure: this.procedure})
      } finally {
        this.loading = false
      }
    }
  },

  mounted() {
    this.refresh()
  },
}
</script>

<style lang="scss" scoped>
.procedure-dump {
  width: 100%;
  height: 100%;
  background: #181818;

  .dump-container {
    width: 100%;
    height: 100%;
    position: relative;
    padding: 1em;
    overflow: auto;
  }

  pre {
    margin: 0;
    padding: 0;
    white-space: pre-wrap;
    word-wrap: break-word;
  }
}
</style>

<template>
  <div class="install-container">
    <div class="install-cmd-container">
      <CopyButton :text="installCmd" />
      <pre><code v-html="highlightedInstallCmd" /></pre>
    </div>
  </div>
</template>

<script>
import 'highlight.js/lib/common'
import 'highlight.js/styles/stackoverflow-dark.min.css'
import hljs from "highlight.js"
import CopyButton from "@/components/elements/CopyButton"
import Utils from "@/Utils"

export default {
  name: "Install",
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
    installCmd() {
      const cmd = this.extension.deps.install_cmd.join('\n').trim()
      return cmd?.length ? cmd : null
    },

    highlightedInstallCmd() {
      return (
        this.installCmd ?
        hljs.highlight(
          'bash',
          this.extension.deps.install_cmd
          .map((cmd) => `$ ${cmd}`)
          .join('\n')
          .trim()
        ).value :
        '# No extra installation steps required'
      )
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common.scss";

.install-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;

  .install-cmd-container {
    width: 100%;
    height: 100%;
    position: relative;
    display: flex;
    flex-direction: column;
    flex-grow: 1;
  }

  pre {
    height: 50%;
  }
}
</style>

<template>
  <div class="install-container">
    <section class="top">
      <header>
        <h2>Dependencies</h2>
      </header>

      <div class="body">
        <div class="container install-cmd-container">
          <CopyButton :text="installCmd" v-if="installCmd" />
          <pre><Loading v-if="loading" /><code v-html="highlightedInstallCmd" v-else /></pre>
        </div>

        <div class="buttons install-btn" v-if="installCmd">
          <RestartButton v-if="installDone" />
          <button type="button"
                  class="btn btn-default"
                  :disabled="installRunning"
                  @click="installExtension">
            <i class="fas fa-download" /> Install
          </button>
        </div>
      </div>
    </section>

    <section class="bottom" v-if="installRunning || installOutput">
      <header>
        <h2>Output</h2>
      </header>

      <div class="body">
        <div class="container install-output" ref="installOutput">
          <CopyButton :text="installOutput" />
          <pre><code v-text="installOutput" /><div
                     class="loading-container"
                     v-if="installRunning">
            <Loading />
          </div></pre>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import 'highlight.js/lib/common'
import 'highlight.js/styles/stackoverflow-dark.min.css'
import hljs from "highlight.js"
import CopyButton from "@/components/elements/CopyButton"
import Loading from "@/components/Loading"
import RestartButton from "@/components/elements/RestartButton"
import Utils from "@/Utils"

export default {
  name: "Install",
  mixins: [Utils],
  emit: ['install-start', 'install-end'],
  components: {
    CopyButton,
    Loading,
    RestartButton,
  },

  props: {
    extension: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      installRunning: false,
      installDone: false,
      installOutput: null,
      installCmds: [],
      pendingCommands: 0,
      error: null,
      loading: false,
    }
  },

  computed: {
    installCmd() {
      if (this.installCmds.length)
        return this.installCmds.join('\n').trim()

      return null
    },

    highlightedInstallCmd() {
      return (
        hljs.highlight(
          this.installCmd ?
          this.installCmds
          .map((cmd) => `$ ${cmd}`)
          .join('\n')
          .trim() :
          '# No extra installation steps required',
          {language: 'bash'}
        ).value
      )
    },
  },

  methods: {
    wsProcess(path) {
      try {
        const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
        const url = `${protocol}://${location.host}${path}`
        const ws = new WebSocket(url)

        ws.onmessage = this.onMessage
        ws.onerror = this.onError
        ws.onclose = this.onClose
      } catch (err) {
        this.notify({
          error: true,
          title: `Websocket initialization error`,
          text: err.toString(),
        })

        console.error('Websocket initialization error')
        console.error(err)
        this.error = err
        this.installRunning = false
      }
    },

    onMessage(msg) {
      if (!this.installOutput)
        this.installOutput = ''

      this.installOutput += msg.data
    },

    onClose() {
      this.installRunning = false
      this.$emit('install-end', this.extension)

      if (!this.error)
        this.installDone = true
        this.notify({
          title: `Extension installed`,
          html: `Extension <b>${this.extension.name}</b> installed successfully`,
          image: {
            iconClass: 'fas fa-check',
          },
        })
    },

    onError(error) {
        this.notify({
          error: true,
          title: `Websocket error`,
          text: error.toString(),
        })

      console.error('Websocket error')
      console.error(error)
      this.error = error
      this.installRunning = false
    },

    installExtension() {
      if (!this.installCmd)
        return

      this.error = null
      this.installRunning = true
      this.installOutput = ''
      this.$emit('install-start', this.extension)

      const cmd = this.installCmds.join(';\n')
      this.request('shell.exec', {
        cmd: cmd,
        ws: true,
      }).then((output) => {
        this.wsProcess(output.ws_path)
      }).catch((err) => {
        this.error = err
        this.installRunning = false
        this.$emit('install-end', this.extension)
      })
    },

    async refreshInstallCmds() {
      this.loading = true
      try {
        this.installCmds = await this.request('application.get_install_commands', {
          extension: this.extension.name,
        })
      } finally {
        this.loading = false
      }
    },
  },

  mounted() {
    this.refreshInstallCmds()
    this.$watch('extension.name', () => {
      this.refreshInstallCmds()
    })

    this.$watch('installOutput', () => {
      this.$nextTick(() => {
        this.$refs.installOutput.focus()
        this.$refs.installOutput.scrollTop = this.$refs.installOutput.scrollHeight
      })
    })
  },
}
</script>

<style lang="scss" scoped>
@import "common.scss";

$header-height: 3.5em;

.install-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;

  section {
    &.top {
      height: 33.3333% !important;
    }

    &.bottom {
      height: 66.6666% !important;
    }

    header {
      height: $header-height;
      padding-left: 0.5em;
      border-top: 1px solid $border-color-1;
      border-bottom: 1px solid $border-color-1;
    }

    .body {
      height: calc(100% - #{$header-height});
      display: flex;
      flex-direction: column;
      padding: 1em;
    }

    h2 {
      font-size: 1.3em;
      opacity: 0.9;
    }
  }

  .container {
    width: 100%;
    height: 100%;
    position: relative;
    display: flex;
    flex-direction: column;
  }

  pre {
    height: 100%;
    position: relative;
    border-radius: 1em;
  }

  :deep(.install-btn) {
    width: 100%;
    margin-top: 1em;
    display: flex;
    justify-content: right;

    button {
      border-radius: 0.5em;
      margin-right: 0.5em;
    }
  }

  .loading-container {
    width: 100%;
    position: relative;

    :deep(.loading) {
      background: none;
    }
  }
}
</style>

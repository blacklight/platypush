<template>
  <div class="file-editor">
    <Loading v-if="loading" />

    <div class="editor-container">
      <div class="editor-highlight-loading" v-if="isProcessing">
        <Loading />
      </div>

      <div class="editor-body">
        <div class="line-numbers" ref="lineNumbers">
          <span class="line-number" v-for="n in lines" :key="n" v-text="n" />
        </div>

        <pre ref="pre"><code ref="content" v-html="displayedContent" /></pre>
        <textarea ref="textarea" v-model="content" @scroll="syncScroll" @input.stop />
      </div>

      <FloatingButton icon-class="fa fa-save"
                      title="Save"
                      :disabled="!hasChanges || saving"
                      @click="saveFile"
                      v-if="withSave" />
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css';

import FloatingButton from "@/components/elements/FloatingButton";
import Highlighter from "./Highlighter";
import Loading from "@/components/Loading";
import Utils from "@/Utils";

export default {
  mixins: [Highlighter, Utils],
  emits: ['save'],
  components: {
    FloatingButton,
    Loading,
  },

  props: {
    file: {
      type: String,
      required: true,
    },

    isNew: {
      type: Boolean,
      default: false,
    },

    withSave: {
      type: Boolean,
      default: true,
    },
  },

  data() {
    return {
      content: '',
      currentContentHash: 0,
      highlightedContent: '',
      highlighting: false,
      highlightTimer: null,
      info: {},
      initialContentHash: 0,
      loading: false,
      saving: false,
      type: null,
    }
  },

  computed: {
    codeClass() {
      return this.type?.length ? `language-${this.type}` : 'language-plaintext'
    },

    displayedContent() {
      return this.highlightedContent?.length ? this.highlightedContent : this.content
    },

    hasChanges() {
      return this.initialContentHash !== this.currentContentHash
    },

    isProcessing() {
      return this.highlighting || this.highlightTimer || this.saving
    },

    lines() {
      if (!this.content?.length) {
        return 1
      }

      return this.content.split('\n').length
    },
  },

  methods: {
    async loadFile() {
      this.setUrlArgs({file: this.file})
      if (this.isNew) {
        this.content = ''
        this.initialContentHash = 0
        this.highlightedContent = ''
        this.info = {}
        this.type = this.getLanguageType({path: this.file})
        return
      }

      this.loading = true

      try {
        this.info = (
          await this.request('file.info', {files: [this.file]})
        )[this.file] || {}

        this.type = this.getLanguageType(this.info)
        this.content = (
          await axios.get(`/file?path=${encodeURIComponent(this.file)}`)
        ).data

        if (typeof this.content === 'object') {
          this.content = JSON.stringify(this.content, null, 2)
        }

        this.initialContentHash = this.content.hashCode()
      } catch (e) {
        this.notify({
          error: true,
          text: e.message,
          title: 'Failed to load file',
        })
      } finally {
        this.loading = false
      }
    },

    async saveFile() {
      if (!this.hasChanges) {
        return
      }

      this.saving = true

      try {
        await axios.put(`/file?path=${encodeURIComponent(this.file)}`, this.content)
        this.initialContentHash = this.content.hashCode()
        this.notify({
          title: 'File saved',
          text: `${this.file} saved`,
          image: {
            icon: 'check',
          },
        })
      } catch (e) {
        this.notify({
          error: true,
          text: e.message,
          title: 'Failed to save file',
        })
      } finally {
        this.saving = false
      }

      this.$emit('save')
    },

    syncScroll(e) {
      const [scrollTop, scrollLeft] = [e.target.scrollTop, e.target.scrollLeft]
      const scrollHeight = Math.min(e.target.scrollHeight, this.$refs.pre.scrollHeight)
      const clientHeight = Math.min(e.target.clientHeight, this.$refs.pre.clientHeight)
      const maxScrollTop = scrollHeight - clientHeight
      const scrollOpts = {
        top: Math.min(scrollTop, maxScrollTop),
        left: scrollLeft,
        behavior: 'auto',
      }

      e.target.scrollTo(scrollOpts)
      this.$refs.pre.scrollTo(scrollOpts)
      this.$refs.lineNumbers.scrollTo({
        top: scrollOpts.top,
        behavior: 'auto',
      })
    },

    highlightContent() {
      this.highlighting = true

      try {
        clearTimeout(this.highlightTimer)
        this.highlightTimer = null
        this.highlightedContent = hljs.highlight(this.content, {language: this.type || 'plaintext'}).value
      } finally {
        this.highlighting = false
      }
    },

    async keyListener(event) {
      if (event.key === 's' && (event.ctrlKey || event.metaKey)) {
        event.preventDefault()
        await this.saveFile()
      }
    },

    addKeyListener() {
      window.addEventListener('keydown', (e) => {
        if (e.key === 's' && (e.ctrlKey || e.metaKey)) {
          e.preventDefault()
          this.saveFile()
        }
      })
    },

    removeKeyListener() {
      window.removeEventListener('keydown', (e) => {
        if (e.key === 's' && (e.ctrlKey || e.metaKey)) {
          e.preventDefault()
          this.saveFile()
        }
      })
    },

    beforeUnload(e) {
      if (this.hasChanges) {
        e.preventDefault()
        e.returnValue = ''
      }
    },

    addBeforeUnload() {
      window.addEventListener('beforeunload', this.beforeUnload)
    },

    removeBeforeUnload() {
      window.removeEventListener('beforeunload', this.beforeUnload)
    },

    reset() {
      this.setUrlArgs({file: null})
      this.removeBeforeUnload()
      this.removeKeyListener()
    },
  },

  watch: {
    file() {
      this.loadFile()
    },

    content() {
      if (!this.content?.length) {
        return
      }

      this.currentContentHash = this.content.hashCode()

      if (!this.highlightedContent?.length) {
        this.highlightContent()
      } else {
        if (this.highlightTimer) {
          clearTimeout(this.highlightTimer)
        }

        this.highlightTimer = setTimeout(this.highlightContent, 1000)

        // Temporarily disable highlighting until the user stops typing,
        // so we don't highlight on every keystroke and we don't lose alignment
        // between the textarea and the pre element.
        this.highlightedContent = this.content
      }
    },
  },

  mounted() {
    this.loadFile()
    this.addBeforeUnload()
    this.addKeyListener()
    this.$nextTick(() => {
      this.$refs.textarea.focus()
    })
  },

  unmouted() {
    this.reset()
  },
}
</script>

<style lang="scss" scoped>
@import "src/style/items";

$line-numbers-width: 2.5em;

.file-editor {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;

  .editor-container,
  .editor-body {
    width: 100%;
    height: 100%;
    position: relative;
    display: flex;
    flex-direction: column;
  }

  .editor-highlight-loading {
    position: absolute;
    top: 0.5em;
    right: 1em;
    width: 10em;
    height: 2em;
    font-size: 0.5em !important;
    display: flex;
    justify-content: center;
    align-items: center;
    opacity: 0.5;
    z-index: 2;

    :deep(.loading) {
      border-radius: 0.5em;
    }
  }

  .editor-body {
    pre, textarea, code, .line-numbers {
      font-family: 'Fira Code', 'Noto Sans Mono', 'Inconsolata', 'Courier New', monospace;
      position: absolute;
      top: 0;
      height: 100%;
      margin: 0;
      white-space: pre;
    }

    .line-numbers {
      width: $line-numbers-width;
      background: $tab-bg;
      border-right: $default-border;
      display: flex;
      flex-direction: column;
      justify-content: flex-start;
      align-items: flex-end;
      overflow: hidden;
      z-index: 2;

      .line-number {
        width: 100%;
        text-align: right;
        padding-right: 0.25em;
      }
    }

    pre, textarea {
      width: calc(100% - #{$line-numbers-width} - 1em);
      left: calc(#{$line-numbers-width} + 1em);
    }

    code {
      width: 100%;
    }

    textarea {
      background: transparent;
      overflow-wrap: normal;
      overflow-x: scroll;
      z-index: 1;
      color: rgba(0, 0, 0, 0);
      caret-color: black;
      border: none;
      outline: none;
    }
  }

  :deep(.floating-btn) {
    z-index: 5;
  }
}
</style>

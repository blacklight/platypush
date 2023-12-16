<template>
  <div class="action-editor-container" :class="{'with-save': withSave}" @click="onClick">
    <Loading v-if="loading" />

    <!-- Action executor container -->
    <div class="action-editor">
      <!-- cURL snippet modal -->
      <div class="curl-modal-container">
        <Modal ref="curlModal" title="curl request" v-if="curlSnippet?.length">
          <div class="output curl-snippet" @click="copyToClipboard(curlSnippet)" >
            <pre><code v-html="highlightedCurlSnippet" /></pre>
          </div>
        </Modal>
      </div>

      <!-- Execute panel views -->
      <div class="header-container">
        <div class="tabs-container">
          <Tabs>
            <Tab :selected="structuredInput" icon-class="fas fa-list" @input="onInputTypeChange(true)">
              Structured
            </Tab>

            <Tab :selected="!structuredInput" icon-class="fas fa-code" @input="onInputTypeChange(false)">
              Raw
            </Tab>
          </Tabs>
        </div>

        <div class="buttons" v-if="withSave">
          <button type="submit" class="save-btn btn-primary"
            :disabled="running || !isValidAction" title="Save"
            @click.stop="onSubmit">
            <i class="fas fa-save" />
          </button>
        </div>
      </div>

      <form ref="actionForm" autocomplete="off" @submit.prevent="onSubmit">
        <!-- Structured request container -->
        <div class="request structured" v-if="structuredInput">
          <!-- Request header -->
          <header>
            <!-- Action autocomplete container -->
            <div class="autocomplete-container">
              <Autocomplete
                ref="autocomplete"
                :items="autocompleteItems"
                @input="updateAction"
                placeholder="Action"
                show-results-when-blank
                autofocus
                :disabled="running"
                :value="action.name" />

              <button :type="withSave ? 'button' : 'submit'" class="run-btn btn-primary"
                :disabled="running || !isValidAction" title="Run" @click.stop="executeAction">
                <i class="fas fa-play" />
              </button>
            </div>
          </header>

          <!-- Action documentation container -->
          <ActionDoc
            :action="action"
            :curl-snippet="curlSnippet"
            :loading="docLoading"
            :doc="selectedDoc"
            @curl-modal="$refs.curlModal.show()" />

          <!-- Action arguments container -->
          <section class="args"
              v-if="action.name in actions && (Object.keys(action.args).length || action.supportsExtraArgs)">
            <h2>
              <i class="fas fa-code" /> &nbsp;
              Arguments
            </h2>

            <ActionArgs :action="action"
                        :loading="loading"
                        :running="running"
                        :selected-arg="selectedArg"
                        :selected-argdoc="selectedArgdoc"
                        @add="addArg"
                        @select="selectArgdoc"
                        @remove="removeArg"
                        @arg-edit="action.args[$event.name].value = $event.value"
                        @extra-arg-name-edit="action.extraArgs[$event.index].name = $event.value"
                        @extra-arg-value-edit="action.extraArgs[$event.index].value = $event.value" />
          </section>

          <!-- Structured response container -->
          <Response :response="response" :error="error" />
        </div>

        <!-- Raw request container -->
        <div class="request raw-request" v-if="!structuredInput">
          <div class="first-row">
            <label>
              <textarea v-model="rawRequest" ref="rawAction" :placeholder="rawRequestPlaceholder" />
            </label>
            <button :type="withSave ? 'button' : 'submit'" :disabled="running"
                    class="raw-run-btn btn-primary" title="Run" @click.stop="executeAction">
              <i class="fas fa-play" />
            </button>
          </div>

          <!-- Raw response container -->
          <Response :response="response" :error="error" />
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import 'highlight.js/lib/common'
import 'highlight.js/styles/stackoverflow-dark.min.css'
import hljs from "highlight.js"
import ActionArgs from "./ActionArgs"
import ActionDoc from "./ActionDoc"
import Autocomplete from "@/components/elements/Autocomplete"
import Loading from "@/components/Loading"
import Modal from "@/components/Modal"
import Response from "./Response"
import Tab from "@/components/elements/Tab"
import Tabs from "@/components/elements/Tabs"
import Utils from "@/Utils"

export default {
  mixins: [Utils],
  emits: ['input'],
  components: {
    ActionArgs,
    ActionDoc,
    Autocomplete,
    Loading,
    Modal,
    Response,
    Tab,
    Tabs,
  },

  props: {
    value: {
      type: Object,
    },

    withSave: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      loading: false,
      running: false,
      docLoading: false,
      structuredInput: true,
      selectedDoc: undefined,
      selectedArg: undefined,
      selectedArgdoc: undefined,
      response: undefined,
      error: undefined,
      rawRequest: undefined,
      rawRequestPlaceholder: 'Raw JSON request. Example:\n\n' +
        '{"type": "request", "action": "file.list", "args": {"path": "/"}}',
      actions: {},
      plugins: {},
      procedures: {},
      actionDocsCache: {},
      action: {
        name: undefined,
        args: {},
        extraArgs: [],
        supportsExtraArgs: false,
      },
    }
  },

  computed: {
    currentActionDocURL() {
      return this.action?.doc_url
    },

    isValidAction() {
      return (
        this.action?.name?.length &&
        this.action.name in this.actions &&
        Object.values(this.action.args).every((arg) => !arg.required || arg.value?.length)
      )
    },

    autocompleteItems() {
      if (this.getPluginName(this.action.name) in this.plugins) {
        return Object.keys(this.actions).sort()
      }

      return Object.keys(this.plugins).sort().map((pluginName) => `${pluginName}.`)
    },

    actionInput() {
      return this.$refs.autocomplete.$el.parentElement.querySelector('input[type=text]')
    },

    requestArgs() {
      if (!this.action.name)
        return {}

      return {
        ...Object.entries(this.action.args).reduce((args, arg) => {
          if (arg[1].value != null) {
            let value = arg[1].value
            try {
              value = JSON.parse(value)
            } catch (e) {
              console.debug('Not a valid JSON value')
              console.debug(value)
            }

            args[arg[0]] = value
          }
          return args
        }, {}),

        ...(this.action.extraArgs || []).reduce((args, arg) => {
          let value = arg.value
          try {
            value = JSON.parse(value)
          } catch (e) {
            console.debug('Not a valid JSON value')
            console.debug(value)
          }

          args[arg.name] = value
          return args
        }, {})
      }
    },

    curlURL() {
      return `${window.location.protocol}//${window.location.host}/execute`
    },

    curlSnippet() {
      if (!this.action.name)
        return ''

      const request = {
        type: 'request',
        action: this.action.name,
        args: this.requestArgs,
      }

      const reqStr = JSON.stringify(request, null, 2)

      return (
        'curl -XPOST -H "Content-Type: application/json" \\\n  ' +
        `-H "Cookie: session_token=${this.getCookies()['session_token']}"`+
        " \\\n  -d '\n  {\n    " +
        this.indent(
          reqStr.split('\n').slice(1, reqStr.length - 2).join('\n'), 2
        ).trim() +
        "' \\\n  " +
        `'${this.curlURL}'`
      )
    },

    highlightedCurlSnippet() {
      return hljs.highlight(
        'bash',
        '# Note: Replace the cookie with a JWT token for production cases\n' +
        this.curlSnippet
      ).value
    },
  },

  methods: {
    async refresh() {
      this.loading = true

      try {
        [this.procedures, this.plugins] = await Promise.all([
          this.request('inspect.get_procedures'),
          this.request('inspect.get_all_plugins'),
        ])
      } finally {
        this.loading = false
      }

      // Register procedures as actions
      this.plugins.procedure = {
        name: 'procedure',
        actions: Object.entries(this.procedures || {}).reduce((actions, [name, procedure]) => {
          actions[name] = {
            name: name,
            args: (procedure.args || []).reduce((args, arg) => {
              args[arg] = {
                name: arg,
                required: false,
              }

              return args
            }, {}),
            supportsExtraArgs: true,
          }

          return actions
        }, {}),
      }

      // Parse actions from the plugins map
      for (const plugin of Object.values(this.plugins)) {
        for (const action of Object.values(plugin.actions)) {
          action.name = plugin.name + '.' + action.name
          action.supportsExtraArgs = !!action.has_kwargs
          delete action.has_kwargs
          this.actions[action.name] = action
        }
      }

      // If an action has been passed on the URL, set it
      const args = this.getUrlArgs()
      const actionName = args?.action
      if (actionName?.length && actionName in this.actions && actionName !== this.action.name) {
        this.updateAction(actionName)
      }
    },

    async updateAction(actionName, params) {
      let {force, args, extraArgs} = params || {}
      if (!args)
        args = {}
      if (!extraArgs)
        extraArgs = []

      if (actionName === this.action.name && !force)
        return

      this.action.name = actionName
      if (!(this.action.name in this.actions)) {
        this.selectedDoc = undefined
        this.resetArgdoc()
        return
      }

      this.resetArgdoc()
      this.docLoading = true

      try {
        this.action = {
          ...this.actions[this.action.name],
          args: Object.entries(this.actions[this.action.name].args).reduce((a, entry) => {
            a[entry[0]] = {
              ...entry[1],
              value: args?.[entry[0]] ?? entry[1].default,
            }

            return a
          }, {}),
          extraArgs: extraArgs || [],
        }
      } finally {
        this.docLoading = false
      }

      this.selectedDoc =
        this.actionDocsCache[this.action.name]?.html ||
        await this.parseDoc(this.action.doc)

      if (!this.actionDocsCache[this.action.name])
        this.actionDocsCache[this.action.name] = {}

      this.actionDocsCache[this.action.name].html = this.selectedDoc
      this.setUrlArgs({action: this.action.name})

      const firstArg = this.$el.querySelector('.action-arg-value')
      if (firstArg) {
        firstArg.focus()
      } else {
        this.$nextTick(() => {
          this.actionInput.focus()
        })
      }

      this.response = undefined
      this.error = undefined
    },

    async parseDoc(docString) {
      if (!docString?.length)
        return docString

      return await this.request('utils.rst_to_html', {text: docString})
    },

    addArg() {
      this.action.extraArgs.push({
        name: undefined,
        value: undefined,
      })
    },

    removeArg(i) {
      this.action.extraArgs.pop(i)
    },

    async selectArgdoc(name) {
      this.selectedArg = name
      this.selectedArgdoc =
        this.actionDocsCache[this.action.name]?.[name]?.html ||
        await this.parseDoc(this.action.args[name].doc)

      if (!this.actionDocsCache[this.action.name])
        this.actionDocsCache[this.action.name] = {}

      this.actionDocsCache[this.action.name][name] = {html: this.selectedArgdoc}
    },

    resetArgdoc() {
      this.selectedArg = undefined
      this.selectedArgdoc = undefined
    },

    onInputTypeChange(structuredInput) {
      this.structuredInput = structuredInput
      this.response = undefined
      this.error = undefined
      this.$nextTick(() => {
        if (structuredInput) {
          this.actionInput.focus()
        } else {
          this.$refs.rawAction.focus()
          if (this.isValidAction) {
            this.rawRequest = JSON.stringify(this.toRequest(this.action), null, 2)
          }
        }
      })
    },

    onResponse(response) {
      this.response = (
        typeof response === 'string' ? response : JSON.stringify(response, null, 2)
      ).trim()

      this.error = undefined
    },

    onError(error) {
      this.response = undefined
      this.error = error
    },

    onDone() {
      this.running = false
    },

    getPluginName(actionName) {
      if (!actionName?.length)
        return ''

      return actionName.split('.').slice(0, -1).join('.')
    },

    executeAction() {
      if (!this.action.name && !this.rawRequest || this.running)
        return

      this.running = true
      if (this.structuredInput) {
        this.request(this.action.name, this.requestArgs).then(this.onResponse).catch(this.onError).finally(this.onDone)
      } else {
        try {
          const request = JSON.parse(this.rawRequest)
          this.execute(request).then(this.onResponse).catch(this.onError).finally(this.onDone)
        } catch (e) {
          this.notify({
            error: true,
            title: 'Invalid JSON request',
            text: e.toString(),
          })
        }
      }
    },

    toRequest(action) {
      return {
        type: 'request',
        action: action.name,
        args: this.requestArgs,
      }
    },

    emitInput(value) {
      value = value || this.value
      if (!value)
        return

      this.$emit("input", this.toRequest(value))
    },

    onClick(event) {
      // Intercept any clicks from RST rendered links and open them in a new tab
      if (event.target.tagName.toLowerCase() === 'a') {
        event.stopPropagation()
        event.preventDefault()
        window.open(event.target.getAttribute('href', '_blank'))
      }
    },

    onValueChanged(value) {
      value = value || this.value
      if (!value)
        return

      const action = value.name || value.action
      this.$nextTick(() => {
        this.updateAction(action, {
          force: true,
          args: value.args || {},
          extraArgs: value.extraArgs || [],
        })
      })
    },

    onSubmit() {
      if (!this.isValidAction)
        return

      if (this.withSave) {
        this.emitInput(this.action)
      } else {
        this.executeAction()
      }
    },
  },

  watch: {
    value: {
      immediate: true,
      handler(value) {
        this.onValueChanged(value)
      },
    },
  },

  async mounted() {
    await this.refresh()
    await this.onValueChanged()
  },
}
</script>

<style lang="scss" scoped>
@import "common";

$btn-width: 3.5em;

.action-editor-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;

  .action-editor {
    width: 100%;
    max-width: 1000px;
    display: flex;
    flex-direction: column;
    box-shadow: $section-shadow;
  }

  .request {
    display: flex;
    flex-direction: column;
    margin: 0 .5em;
  }

  .run-btn {
    width: $btn-width;
    height: 2.5em;
    background: $background-color;
    border-color: $border-color-3;
    border-left: none;
    border-radius: 0 1em 1em 0;
    padding: .5em 1em;
    box-shadow: none;
    cursor: pointer;

    &:hover {
      background: $hover-bg;
      border-color: $active-glow-bg-2;
      box-shadow: none;
    }

    &:disabled {
      opacity: 0.7;
      color: $default-fg-2; 
      cursor: initial;
      box-shadow: none;

      &:hover {
        background: $background-color;
        box-shadow: none;
      }
    }
  }

  .raw-run-btn {
    padding: .5em 1.5em;
    border-radius: 1em;
  }

  .curl-modal-container {
    :deep(.modal) {
      .content {
        width: 100%;
      }

      .content .body {
        height: auto;
      }

      .output {
        border-radius: 0;
      }
    }
  }

  .autocomplete-container {
    display: flex;
    flex-direction: row;
    align-items: center;

    :deep(.autocomplete) {
      width: calc(100% - $btn-width);

      input[type=text] {
        height: 2.5em;
        border-radius: 1em 0 0 1em;
        box-shadow: none;
      }
    }
  }

  .raw-request {
    height: 100%;
    overflow: auto;

    textarea {
      width: 100%;
      min-height: 15em;
      border: $default-border-2;
      box-shadow: $border-shadow-bottom;
      padding: 1em;
      font-family: monospace;
      font-size: 0.9em;
    }
  }

  &.with-save {
    .header-container {
      width: 100%;
      height: $tab-height;
      display: flex;
      flex-direction: row;
      background: $tabs-bg;
      border-bottom: 1px solid $border-color-3;
      box-shadow: $border-shadow-bottom;

      .buttons {
        width: $btn-width;
        height: calc($tab-height - 1px);
        background: $tab-bg;

        button {
          width: $btn-width;
          height: $tab-height;

          &:disabled {
            opacity: 0.7;
            background: $default-bg-6;
            cursor: initial;
            box-shadow: none;

            &:hover {
              background: $tab-bg;
              box-shadow: none;
            }
          }
        }
      }

      .tabs-container {
        width: calc(100% - $btn-width);

        :deep(.tabs) {
          width: 100%;
          height: calc($tab-height - 1px);
          box-shadow: none;

          @include until($tablet) {
            .tab {
              width: 50%;
              flex-grow: 0;
            }
          }
        }
      }
    }
  }
}
</style>

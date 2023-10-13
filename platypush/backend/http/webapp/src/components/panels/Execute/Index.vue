<template>
  <div class="row plugin execute-container" @click="onClick">
    <Loading v-if="loading" />

    <!-- Action executor container -->
    <main>
      <h1>Execute Action</h1>

      <!-- cURL snippet modal -->
      <Modal ref="curlModal" title="curl request" v-if="curlSnippet?.length">
        <div class="output curl-snippet" @click="copyToClipboard(curlSnippet)" >
          <pre><code v-html="highlightedCurlSnippet" /></pre>
        </div>
      </Modal>

      <!-- Execute panel views -->
      <Tabs>
        <Tab :selected="structuredInput" icon-class="fas fa-list" @input="onInputTypeChange(true)">
          Structured
        </Tab>

        <Tab :selected="!structuredInput" icon-class="fas fa-code" @input="onInputTypeChange(false)">
          Raw
        </Tab>
      </Tabs>

      <form ref="actionForm" autocomplete="off" @submit.prevent="executeAction">
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
            </div>
            <div class="buttons">
              <button type="submit" class="run-btn btn-primary"
                :disabled="running || !action?.name?.length" title="Run">
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
            <button type="submit" :disabled="running" class="run-btn btn-primary" title="Run">
              <i class="fas fa-play" />
            </button>
          </div>

          <!-- Raw response container -->
          <Response :response="response" :error="error" />
        </div>
      </form>
    </main>
  </div>
</template>

<script>
import 'highlight.js/lib/common'
import 'highlight.js/styles/stackoverflow-dark.css'
import hljs from "highlight.js"
import ActionArgs from "./ActionArgs"
import ActionDoc from "./ActionDoc"
import Autocomplete from "@/components/elements/Autocomplete"
import Loading from "@/components/Loading"
import Modal from "@/components/Modal";
import Response from "./Response"
import Tab from "@/components/elements/Tab"
import Tabs from "@/components/elements/Tabs"
import Utils from "@/Utils"

export default {
  name: "Execute",
  mixins: [Utils],
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

        ...this.action.extraArgs.reduce((args, arg) => {
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
    },

    async updateAction(actionName) {
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
          args: Object.entries(this.actions[this.action.name].args).reduce((args, entry) => {
            args[entry[0]] = {
              ...entry[1],
              value: entry[1].default,
            }

            return args
          }, {}),
          extraArgs: [],
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

      this.$el.querySelector('.action-arg-value')?.focus()
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

    onClick(event) {
      // Intercept any clicks from RST rendered links and open them in a new tab
      if (event.target.tagName.toLowerCase() === 'a') {
        event.stopPropagation()
        event.preventDefault()
        window.open(event.target.getAttribute('href', '_blank'))
      }
    },
  },

  mounted() {
    this.refresh()
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.execute-container {
  width: 100%;
  height: 100%;
  color: $default-fg-2;
  font-weight: 400;
  border-radius: 0 0 1em 1em;
  display: flex;
  flex-direction: column;
  align-items: center;

  main {
    width: 100%;
    max-width: 1000px;
    display: flex;
    flex-direction: column;
    box-shadow: $section-shadow;

    @include from($desktop) {
      margin: 1em;
      border-radius: 1em 1em 0 0;
    }
  }

  .request {
    display: flex;
    flex-direction: column;
    margin: 0 .5em;
  }

  .run-btn {
    background: $background-color;
    border-radius: .25em;
    padding: .5em 1.5em;
    box-shadow: $primary-btn-shadow;
    cursor: pointer;

    &:hover {
      background: $hover-bg;
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
}
</style>

<template>
  <div class="row plugin execute-container" @click="onClick">
    <Loading v-if="loading" />

    <!-- Action executor container -->
    <main>
      <h1>Execute Action</h1>

      <!-- cURL snippet modal -->
      <Modal ref="curlModal" title="curl request" v-if="curlSnippet?.length">
        <textarea class="output curl-snippet" readonly :value="curlSnippet"
          @click="copyToClipboard(curlSnippet)" />
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
          <section class="doc-container" v-if="selectedDoc">
            <h2>
              <div class="title">
                <i class="fas fa-book" /> &nbsp;
                <a :href="this.action?.doc_url">Action documentation</a>
              </div>
              <div class="buttons" v-if="action?.name">
                <button type="button" title="cURL command" v-if="curlSnippet?.length"
                        @click="$refs.curlModal.show()">
                  <i class="fas fa-terminal" />
                </button>
              </div>
            </h2>

            <div class="doc html">
              <Loading v-if="docLoading" />
              <span v-html="selectedDoc" v-else />
            </div>
          </section>

          <!-- Action arguments container -->
          <section class="args"
              v-if="action.name in actions && (Object.keys(action.args).length || action.supportsExtraArgs)">
            <h2>
              <i class="fas fa-code" /> &nbsp;
              Arguments
            </h2>

            <div class="args-body">
              <div class="args-list"
                   v-if="Object.keys(action.args).length || action.supportsExtraArgs">
                <!-- Supported action arguments -->
                <div class="arg" :key="name" v-for="name in Object.keys(action.args)">
                  <label>
                    <input
                        type="text"
                        class="action-arg-value"
                        :class="{required: action.args[name].required}"
                        :disabled="running"
                        :placeholder="name"
                        v-model="action.args[name].value"
                        @focus="selectArgdoc(name)">
                    <span class="required-flag" v-if="action.args[name].required">*</span>
                  </label>

                  <Argdoc :name="selectedArg"
                          :args="action.args[selectedArg]"
                          :doc="selectedArgdoc"
                          :loading="docLoading"
                          is-mobile
                          v-if="selectedArgdoc && selectedArg && name === selectedArg" />
                </div>

                <!-- Extra action arguments -->
                <div class="extra-args" v-if="Object.keys(action.extraArgs).length">
                  <div class="arg extra-arg" :key="i" v-for="i in Object.keys(action.extraArgs)">
                    <label class="col-5">
                      <input type="text" class="action-extra-arg-name" :disabled="running"
                             placeholder="Name" v-model="action.extraArgs[i].name">
                    </label>
                    <label class="col-6">
                      <input type="text" class="action-extra-arg-value" :disabled="running"
                             placeholder="Value" v-model="action.extraArgs[i].value">
                    </label>
                    <label class="col-1 buttons">
                      <button type="button" class="action-extra-arg-del" title="Remove argument"
                              @click="removeArg(i)">
                        <i class="fas fa-trash" />
                      </button>
                    </label>
                  </div>
                </div>

                <div class="add-arg" v-if="action.supportsExtraArgs">
                  <button type="button" title="Add an argument" @click="addArg">
                    <i class="fas fa-plus" />
                  </button>
                </div>
              </div>

              <Argdoc :name="selectedArg"
                      :args="action.args[selectedArg]"
                      :doc="selectedArgdoc"
                      :loading="docLoading"
                      v-if="selectedArgdoc && selectedArg" />
            </div>
          </section>

          <section class="response">
            <h2 v-if="error != null || response != null">
              <span class="title">
                {{ error != null ? 'Error' : 'Output' }}
              </span>
              <span class="buttons">
                <button type="button" title="Copy to clipboard" @click="copyToClipboard(response)">
                  <i class="fas fa-clipboard" />
                </button>
              </span>
            </h2>
            <div class="output response" v-if="response != null">
              <pre v-text="response" />
            </div>

            <div class="output error" v-else-if="error != null">
              <pre v-text="error" />
            </div>
          </section>
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

          <section class="response" v-if="response != null || error != null">
            <hgroup v-if="error != null || response != null">
              <h2 v-text="error != null ? 'Error' : 'Output'" />
              <div class="buttons">
                <button type="button" title="Copy to clipboard" @click="copyToClipboard(error)">
                  <i class="fas fa-clipboard" />
                </button>
              </div>
            </hgroup>
            <div class="error" v-html="error" v-if="error != null" />
            <div class="response" v-html="response" v-else-if="response != null" />
          </section>
        </div>
      </form>
    </main>

    <!-- Procedures section (to be removed) -->
    <div class="section procedures-container" v-if="Object.keys(procedures).length">
      <h1>Execute Procedure</h1>
      <div class="procedure" :class="selectedProcedure.name === name ? 'selected' : ''"
           v-for="name in Object.keys(procedures).sort()" :key="name" @click="updateProcedure(name, $event)">
        <form ref="procedureForm" autocomplete="off" @submit.prevent="executeProcedure">
          <div class="head">
            <div class="name col-no-margin-11" v-text="name" />
            <div class="btn-container col-no-margin-1">
              <button type="submit" class="run-btn btn-default" :disabled="running" title="Run"
                      @click.stop="$emit('submit')" v-if="selectedProcedure.name === name">
                <i class="fas fa-play" />
              </button>
            </div>
          </div>

          <div class="args-list" v-if="selectedProcedure.name === name">
            <div class="arg"
                 v-for="argname in Object.keys(selectedProcedure.args)"
                 :key="argname">
              <label>
                <input type="text" class="action-arg-value" @click="$event.stopPropagation()" :disabled="running"
                       :placeholder="argname" v-model="selectedProcedure.args[argname]">
              </label>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import Argdoc from "./Argdoc"
import Autocomplete from "@/components/elements/Autocomplete"
import Loading from "@/components/Loading"
import Modal from "@/components/Modal";
import Tab from "@/components/elements/Tab"
import Tabs from "@/components/elements/Tabs"
import Utils from "@/Utils"

export default {
  name: "Execute",
  components: {Argdoc, Autocomplete, Loading, Modal, Tab, Tabs},
  mixins: [Utils],

  data() {
    return {
      loading: false,
      running: false,
      docLoading: false,
      structuredInput: true,
      selectedDoc: undefined,
      selectedArg: undefined,
      selectedArgdoc: undefined,
      selectedProcedure: {
        name: undefined,
        args: {},
      },

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
          let value = args[arg.value]
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

      return (
        'curl -XPOST -H "Content-Type: application/json" \\\n\t' +
        `-H "Cookie: session_token=${this.getCookies()['session_token']}"`+
        " \\\n\t -d '" +
        this.indent(JSON.stringify(request, null, 2), 2).trim() + "' \\\n\t" +
        `'${this.curlURL}'`
      )
    },
  },

  methods: {
    async refresh() {
      this.loading = true

      try {
        this.procedures = await this.request('inspect.get_procedures')
        this.plugins = await this.request('inspect.get_all_plugins')
      } finally {
        this.loading = false
      }

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

    updateProcedure(name, event) {
      if (event.target.getAttribute('type') === 'submit') {
        return
      }

      if (this.selectedProcedure.name === name) {
        this.selectedProcedure = {
          name: undefined,
          args: {},
        }

        return
      }

      if (!(name in this.procedures)) {
        console.warn('Procedure not found: ' + name)
        return
      }

      this.selectedProcedure = {
        name: name,
        args: (this.procedures[name].args || []).reduce((args, arg) => {
          args[arg] = undefined
          return args
        }, {})
      }
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

    executeProcedure(event) {
      if (!this.selectedProcedure.name || this.running)
        return

      event.stopPropagation()
      this.running = true
      const args = {
        ...Object.entries(this.selectedProcedure.args).reduce((args, arg) => {
          if (arg[1] != null) {
            let value = arg[1]
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
      }

      this.request('procedure.' + this.selectedProcedure.name, args)
          .then(this.onResponse).catch(this.onError).finally(this.onDone)
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

  .procedures-container {
    .procedure {
      background: $background-color;
      border-bottom: $default-border-2;
      padding: 1.5em .5em;
      cursor: pointer;

      &:hover {
        background: $hover-bg;
      }

      &.selected {
        background: $selected-bg;
      }

      form {
        background: none;
        display: flex;
        margin-bottom: 0 !important;
        flex-direction: column;
        box-shadow: none;
      }

      .head {
        display: flex;
        align-items: center;
      }

      .btn-container {
        text-align: right;
      }

      button {
        background: $procedure-submit-btn-bg;
      }
    }

    .action-arg-value {
      margin: 0.25em 0;
    }
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

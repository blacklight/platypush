<template>
  <div class="row plugin execute-container">
    <Loading v-if="loading" />
    <div class="command-container">
      <div class="title">Execute Action</div>
      <form class="action-form" ref="actionForm" autocomplete="off" @submit.prevent="executeAction">
        <div class="request-type-container">
          <input type="radio" id="action-structured-input"
                 :checked="structuredInput" @change="onInputTypeChange(true)">
          <label for="action-structured-input">Structured request</label>
          <input type="radio" id="action-raw-input"
                 :checked="!structuredInput" @change="onInputTypeChange(false)">
          <label for="action-raw-input">Raw request</label>
        </div>

        <div class="request structured-request" :class="structuredInput ? '' : 'hidden'">
          <div class="autocomplete">
            <label>
              <input ref="actionName" type="text" class="action-name"
                     placeholder="Action Name" :disabled="running" v-model="action.name"
                     @change="actionChanged=true" @blur="updateAction">
            </label>
          </div>
          <button type="submit" class="run-btn btn-primary" :disabled="running" title="Run">
            <i class="fas fa-play" />
          </button>

          <div class="doc-container" v-if="selectedDoc">
            <div class="title">
              Action documentation
            </div>

            <div class="doc html" v-html="selectedDoc" v-if="htmlDoc" />
            <div class="doc raw" v-text="selectedDoc" v-else />
          </div>

          <div class="options" v-if="action.name in actions && (Object.keys(action.args).length ||
              action.supportsExtraArgs)">
            <div class="params" ref="params"
                 v-if="Object.keys(action.args).length || action.supportsExtraArgs">
              <div class="param" :key="name" v-for="name in Object.keys(action.args)">
                <label>
                  <input type="text" class="action-param-value" :disabled="running"
                         :placeholder="name" v-model="action.args[name].value"
                         @focus="selectAttrDoc(name)"
                         @blur="resetAttrDoc">
                </label>

                <div class="attr-doc-container mobile" v-if="selectedAttrDoc && selectedAttr === name">
                  <div class="title">
                    Attribute: <div class="attr-name" v-text="selectedAttr" />
                  </div>

                  <div class="doc html" v-html="selectedAttrDoc" v-if="htmlDoc" />
                  <div class="doc raw" v-text="selectedAttrDoc" v-else />
                </div>
              </div>

              <div class="extra-params" ref="extraParams" v-if="Object.keys(action.extraArgs).length">
                <div class="param extra-param" :key="i" v-for="i in Object.keys(action.extraArgs)">
                  <label class="col-5">
                    <input type="text" class="action-extra-param-name" :disabled="running"
                           placeholder="Name" v-model="action.extraArgs[i].name">
                  </label>
                  <label class="col-5">
                    <input type="text" class="action-extra-param-value" :disabled="running"
                           placeholder="Value" v-model="action.extraArgs[i].value">
                  </label>
                  <label class="col-2 buttons">
                    <button type="button" class="action-extra-param-del" title="Remove parameter"
                            @click="removeParameter(i)">
                      <i class="fas fa-trash" />
                    </button>
                  </label>
                </div>
              </div>

              <div class="add-param" v-if="action.supportsExtraArgs">
                <button type="button" title="Add a parameter" @click="addParameter">
                  <i class="fas fa-plus" />
                </button>
              </div>
            </div>

            <div class="attr-doc-container widescreen" v-if="selectedAttrDoc">
              <div class="title">
                Attribute: <div class="attr-name" v-text="selectedAttr" />
              </div>

              <div class="doc html" v-html="selectedAttrDoc" v-if="htmlDoc" />
              <div class="doc raw" v-text="selectedAttrDoc" v-else />
            </div>

            <div class="output-container">
              <div class="title" v-text="error != null ? 'Error' : 'Output'" v-if="error != null || response != null" />
              <div class="response" v-html="response" v-if="response != null" />
              <div class="error" v-html="error" v-else-if="error != null" />
            </div>
          </div>
        </div>

        <div class="request raw-request" :class="structuredInput ? 'hidden' : ''">
          <div class="first-row">
            <label>
              <textarea v-model="rawRequest" placeholder="Raw JSON request" />
            </label>
            <button type="submit" :disabled="running" class="run-btn btn-primary" title="Run">
              <i class="fas fa-play" />
            </button>
          </div>

          <div class="output-container" v-if="response != null || error != null">
            <div class="title" v-text="error != null ? 'Error' : 'Output'" />
            <div class="error" v-html="error" v-if="error != null" />
            <div class="response" v-html="response" v-else-if="response != null" />
          </div>
        </div>
      </form>
    </div>

    <div class="procedures-container">
      <div class="title">Execute Procedure</div>
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

          <div class="params" v-if="selectedProcedure.name === name">
            <div class="param"
                 v-for="argname in Object.keys(selectedProcedure.args)"
                 :key="argname">
              <label>
                <input type="text" class="action-param-value" @click="$event.stopPropagation()" :disabled="running"
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
import autocomplete from "@/components/elements/Autocomplete"
import Utils from "@/Utils"
import Loading from "@/components/Loading";

export default {
  name: "Execute",
  components: {Loading},
  mixins: [Utils],

  data() {
    return {
      loading: false,
      running: false,
      structuredInput: true,
      actionChanged: false,
      selectedDoc: undefined,
      selectedAttr: undefined,
      selectedAttrDoc: undefined,
      selectedProcedure: {
        name: undefined,
        args: {},
      },

      response: undefined,
      error: undefined,
      htmlDoc: false,
      rawRequest: undefined,
      actions: {},
      plugins: {},
      procedures: {},
      action: {
        name: undefined,
        args: {},
        extraArgs: [],
        supportsExtraArgs: false,
      },
    }
  },

  methods: {
    async refresh() {
      this.loading = true

      try {
        this.procedures = await this.request('inspect.get_procedures')
        this.plugins = await this.request('inspect.get_all_plugins', {html_doc: false})
      } finally {
        this.loading = false
      }

      for (const plugin of Object.values(this.plugins)) {
        if (plugin.html_doc)
          this.htmlDoc = true

        for (const action of Object.values(plugin.actions)) {
          action.name = plugin.name + '.' + action.name
          action.supportsExtraArgs = !!action.has_kwargs
          delete action.has_kwargs
          this.actions[action.name] = action
        }
      }

      const self = this
      autocomplete(this.$refs.actionName, Object.keys(this.actions).sort(), (evt, value) => {
        this.action.name = value
        self.updateAction()
      })
    },

    updateAction() {
      if (!(this.action.name in this.actions))
        this.selectedDoc = undefined

      if (!this.actionChanged || !(this.action.name in this.actions))
        return

      this.loading = true
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
        this.loading = false
      }

      this.selectedDoc = this.parseDoc(this.action.doc)
      this.actionChanged = false
      this.response = undefined
      this.error = undefined
    },

    parseDoc(docString) {
      if (!docString?.length || this.htmlDoc)
        return docString

      let lineNo = 0
      let trailingSpaces = 0

      return docString.split('\n').reduce((doc, line) => {
        if (++lineNo === 2)
          trailingSpaces = line.match(/^(\s*)/)[1].length

        if (line.trim().startsWith('.. code-block'))
          return doc

        doc += line.slice(trailingSpaces).replaceAll('``', '') + '\n'
        return doc
      }, '')
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

    addParameter() {
      this.action.extraArgs.push({
        name: undefined,
        value: undefined,
      })
    },

    removeParameter(i) {
      this.action.extraArgs.pop(i)
    },

    selectAttrDoc(name) {
      this.response = undefined
      this.error = undefined
      this.selectedAttr = name
      this.selectedAttrDoc = this.parseDoc(this.action.args[name].doc)
    },

    resetAttrDoc() {
      this.response = undefined
      this.error = undefined
      this.selectedAttr = undefined
      this.selectedAttrDoc = undefined
    },

    onInputTypeChange(structuredInput) {
      this.structuredInput = structuredInput
      this.response = undefined
      this.error = undefined
    },

    onResponse(response) {
      this.response = '<pre>' + JSON.stringify(response, null, 2) + '</pre>'
      this.error = undefined
    },

    onError(error) {
      this.response = undefined
      this.error = error
    },

    onDone() {
      this.running = false
    },

    executeAction() {
      if (!this.action.name && !this.rawRequest || this.running)
        return

      this.running = true
      if (this.structuredInput) {
        const args = {
          ...Object.entries(this.action.args).reduce((args, param) => {
            if (param[1].value != null) {
              let value = param[1].value
              try {
                value = JSON.parse(value)
              } catch (e) {
                console.debug('Not a valid JSON value')
                console.debug(value)
              }

              args[param[0]] = value
            }
            return args
          }, {}),

          ...this.action.extraArgs.reduce((args, param) => {
            let value = args[param.value]
            try {
              value = JSON.parse(value)
            } catch (e) {
              console.debug('Not a valid JSON value')
              console.debug(value)
            }

            args[param.name] = value
            return args
          }, {})
        }

        this.request(this.action.name, args).then(this.onResponse).catch(this.onError).finally(this.onDone)
      } else {
        let request = this.rawRequest
        try {
          request = JSON.parse(this.rawRequest)
        } catch (e) {
          this.notify({
            error: true,
            title: 'Invalid JSON request',
            text: e.toString(),
          })

          return
        }

        this.execute(request).then(this.onResponse).catch(this.onError).finally(this.onDone)
      }
    },

    executeProcedure(event) {
      if (!this.selectedProcedure.name || this.running)
        return

      event.stopPropagation()
      this.running = true
      const args = {
        ...Object.entries(this.selectedProcedure.args).reduce((args, param) => {
          if (param[1] != null) {
            let value = param[1]
            try {
              value = JSON.parse(value)
            } catch (e) {
              console.debug('Not a valid JSON value')
              console.debug(value)
            }

            args[param[0]] = value
          }
          return args
        }, {}),
      }

      this.request('procedure.' + this.selectedProcedure.name, args)
          .then(this.onResponse).catch(this.onError).finally(this.onDone)
    },
  },

  mounted() {
    this.refresh()
  },
}
</script>

<style lang="scss">
@import "vars";
@import "~@/style/autocomplete.scss";

$params-desktop-width: 30em;
$params-tablet-width: 20em;

.execute-container {
  width: 100%;
  height: 100%;
  color: $default-fg-2;
  font-weight: 400;
  border-bottom: $default-border-2;
  border-radius: 0 0 1em 1em;

  form {
    padding: 0;
    margin: 0;
    border-radius: 0;
    border: none;
  }

  .action-form {
    padding: 1em .5em;
  }

  .title {
    background: $title-bg;
    padding: .5em;
    border: $title-border;
    box-shadow: $title-shadow;
    font-size: 1.1em;
    margin-bottom: 0 !important;
  }

  .request-type-container {
    display: flex;
    flex-direction: row;
    align-items: baseline;

    label {
      margin: 0 1em 0 .5em;
    }
  }

  .request {
    margin: 0 .5em;

    form {
      margin-bottom: 0 !important;
    }

    .autocomplete {
      width: 80%;
      max-width: 60em;
    }

    .action-name {
      box-shadow: $action-name-shadow;
      width: 100%;
    }

    [type=submit] {
      margin-left: 2em;
    }

    .options {
      display: flex;
      margin-top: .5em;
      margin-bottom: 1.5em;
      padding-top: .5em;

      @include until($tablet) {
        flex-direction: column;
      }
    }

    .params {
      @include until($tablet) {
        width: 100%;
      }

      @include from($tablet) {
        width: $params-tablet-width;
        margin-right: 1.5em;
      }

      @include from($desktop) {
        width: $params-desktop-width;
      }

      .param {
        margin-bottom: .25em;
        @include until($tablet) {
          width: 100%;
        }
      }

      .action-param-value {
        width: 100%;
      }
    }

    .add-param {
      width: 100%;

      button {
        width: 100%;
        background: $extra-params-btn-bg;
        border: $title-border;
      }
    }

    .extra-param {
      display: flex;
      margin-bottom: .5em;

      .action-extra-param-del {
        border: 0;
        text-align: right;
        padding: 0 .5em;
      }

      .buttons {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: .25em;

        button {
          background: none;

          &:hover {
            color: $default-hover-fg;
          }
        }
      }
    }

    .doc-container,
    .output-container {
      margin-top: .5em;
      .doc {
        &.raw {
          white-space: pre;
        }
      }
    }

    .attr-doc-container {
      @include from($tablet) {
        width: calc(100% - #{$params-tablet-width} - 2em);
      }

      @include from($desktop) {
        width: calc(100% - #{$params-desktop-width} - 2em);
      }

      .doc {
        white-space: pre-line;
        width: 100%;
        overflow: auto;
      }

      &.widescreen {
        @include until($tablet) {
          display: none;
        }
      }

      &.mobile {
        width: 100%;
        @include from($tablet) {
          display: none;
        }
      }
    }

    .doc-container,
    .attr-doc-container {
      .doc {
        padding: 1em !important;

        &.raw {
          font-family: monospace;
          font-size: .8em;
        }
      }
    }

    .output-container, .doc-container, .attr-doc-container {
      max-height: 50vh;
      display: flex;
      flex-direction: column;

      .title {
        font-weight: normal;
        font-size: 1em;
        padding: .5em;
        background: $section-title-bg;
        border-radius: .5em;

        .attr-name {
          display: inline-block;
          font-weight: bold;
        }
      }

      .response,
      .error,
      .doc {
        height: 100%;
        padding: .5em .5em 0 .5em;
        border-radius: 0 0 1em 1em;
        overflow: auto;
      }

      .response {
        background: $response-bg;
        border: $response-border;
      }

      .error {
        background: $error-bg;
        border: $error-border;
      }

      .doc {
        background: $doc-bg;
        border: $doc-border;
      }
    }

    textarea {
      width: 100%;
      height: 10em;
      margin-bottom: .5em;
      padding: .5em;
      border: $default-border-2;
      border-radius: 1em;
      box-shadow: $border-shadow-bottom-right;
      outline: none;

      &:hover {
        border: 1px solid $default-hover-fg-2;
      }

      &:focus {
        border: 1px solid $selected-fg;
      }
    }
  }

  .raw-request {
    .first-row {
      @include until($tablet) {
        width: 100%;
      }

      @include from($tablet) {
        width: 80%;
        max-width: 60em;
      }

      display: flex;
      flex-direction: column;

      button {
        margin-left: 0;
      }
    }
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
  }

  pre {
    background: none;
  }

  .run-btn {
    border-radius: 2em;
    padding: .5em .75em;

    &:hover {
      opacity: .8;
    }
  }
}
</style>

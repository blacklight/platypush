<template>
  <div class="entity procedure-container">
    <div class="head" :class="{collapsed: collapsed_}" @click="onHeaderClick">
      <div class="icon">
        <EntityIcon :entity="value" :icon="icon" :loading="loading" />
      </div>

      <div class="label">
        <div class="name" v-text="value.name" />
      </div>

      <div class="value-and-toggler">
        <div class="value">
          <button class="btn btn-primary head-run-btn"
                  title="Run Procedure"
                  :disabled="loading"
                  @click.stop="run"
                  v-if="collapsed_">
            <i class="fas fa-play" />
          </button>
        </div>

        <div class="collapse-toggler" @click.stop="collapsed_ = !collapsed_">
          <i class="fas" :class="{'fa-chevron-down': collapsed_, 'fa-chevron-up': !collapsed_}" />
        </div>
      </div>
    </div>

    <div class="body" v-if="!collapsed_" @click.stop>
      <section class="run">
        <header :class="{collapsed: runCollapsed}" @click="runCollapsed = !runCollapsed">
          <span class="col-10">
            <i class="fas fa-play" />&nbsp; Run
          </span>
          <span class="col-2 buttons">
            <button type="button"
                    class="btn btn-primary"
                    :disabled="loading"
                    :title="runCollapsed ? 'Expand' : 'Collapse'">
              <i class="fas" :class="{'fa-chevron-down': runCollapsed, 'fa-chevron-up': !runCollapsed}" />
            </button>
          </span>
        </header>

        <div class="run-body" v-if="!runCollapsed">
          <form @submit.prevent="run">
            <div class="args" v-if="value.args?.length">
              Arguments
              <div class="row arg" v-for="(arg, index) in value.args || []" :key="index">
                <input type="text"
                       class="argname"
                       :value="arg"
                       :disabled="true" />&nbsp;=
                <input type="text"
                       class="argvalue"
                       placeholder="Value"
                       :disabled="loading"
                       @input="updateArg(arg, $event)" />
              </div>
            </div>

            <div class="extra args">
              Extra Arguments
              <div class="row arg" v-for="(value, name) in extraArgs" :key="name">
                <input type="text"
                       class="argname"
                       placeholder="Name"
                       :value="name"
                       :disabled="loading"
                       @blur="updateExtraArgName(name, $event)" />&nbsp;=
                <input type="text"
                       placeholder="Value"
                       class="argvalue"
                       :value="value"
                       :disabled="loading"
                       @input="updateExtraArgValue(arg, $event)" />
              </div>

              <div class="row add-arg">
                <input type="text"
                       class="argname"
                       placeholder="Name"
                       v-model="newArgName"
                       :disabled="loading"
                       ref="newArgName"
                       @blur="addExtraArg" />&nbsp;=
                <input type="text"
                       class="argvalue"
                       placeholder="Value"
                       v-model="newArgValue"
                       :disabled="loading"
                       @blur="addExtraArg" />
              </div>
            </div>

            <div class="row run-container">
              <button type="submit"
                      class="btn btn-primary"
                      :disabled="loading"
                      title="Run Procedure">
                <i class="fas fa-play" />
              </button>
            </div>
          </form>

          <div class="response-container" v-if="lastResponse || lastError">
            <Response :response="lastResponse" :error="lastError" />
          </div>
        </div>
      </section>

      <section class="info">
        <header :class="{collapsed: infoCollapsed}" @click="infoCollapsed = !infoCollapsed">
          <span class="col-10">
            <i class="fas fa-info-circle" />&nbsp; Info
          </span>
          <span class="col-2 buttons">
            <button type="button"
                    class="btn btn-primary"
                    :disabled="loading"
                    :title="infoCollapsed ? 'Expand' : 'Collapse'">
              <i class="fas" :class="{'fa-chevron-down': infoCollapsed, 'fa-chevron-up': !infoCollapsed}" />
            </button>
          </span>
        </header>

        <div class="info-body" v-if="!infoCollapsed">
          <div class="item">
            <div class="label">Source</div>
            <div class="value">
              <i :class="procedureTypeIconClass" />&nbsp;
              {{ value.procedure_type }}
            </div>
          </div>

          <div class="item">
            <IconEditor :entity="value" />
          </div>

          <div class="item actions" v-if="value?.actions?.length">
            <div class="label">Actions</div>
            <div class="value">
              <div class="item">
                <button type="button"
                        class="btn btn-primary"
                        title="Edit Actions"
                        :disabled="loading"
                        @click="showProcedureEditor = !showProcedureEditor">
                  <span v-if="isReadOnly && !showProcedureEditor">
                    <i class="fas fa-eye" />&nbsp; View
                  </span>
                  <span v-else-if="!isReadOnly && !showProcedureEditor">
                    <i class="fas fa-edit" />&nbsp; Edit
                  </span>
                  <span v-else>
                    <i class="fas fa-times" />&nbsp; Close
                  </span>
                </button>
              </div>

              <div class="item delete" v-if="!isReadOnly">
                <button type="button"
                        title="Delete Procedure"
                        :disabled="loading"
                        @click="showConfirmDelete = true">
                  <i class="fas fa-trash" />&nbsp; Delete
                </button>
              </div>
            </div>
          </div>

          <div class="item" v-if="value.source">
            <div class="label">Path</div>
            <div class="value">
              <a :href="$route.path" @click.prevent="showFileEditor = true">
                {{ displayPath }}
              </a>
            </div>
          </div>
        </div>
      </section>
    </div>

    <div class="file-editor-container" v-if="showFileEditor && value.source">
      <FileEditor :file="value.source"
                  :line="value.line"
                  :visible="true"
                  :uppercase="false"
                  @close="showFileEditor = false" />
    </div>

    <ProcedureEditor :procedure="value"
                     :read-only="isReadOnly"
                     :with-name="!isReadOnly"
                     :with-save="!isReadOnly"
                     :value="value"
                     :visible="showProcedureEditor"
                     @input="onUpdate"
                     @close="showProcedureEditor = false"
                     ref="editor"
                     v-if="value?.actions?.length && showProcedureEditor" />

    <div class="confirm-delete-container">
      <ConfirmDialog :visible="true"
                     @input="remove"
                     @close="showConfirmDelete = false"
                     v-if="showConfirmDelete">
        Are you sure you want to delete the procedure <b>{{ value.name }}</b>?
      </ConfirmDialog>
    </div>
  </div>
</template>

<script>
import ConfirmDialog from "@/components/elements/ConfirmDialog";
import EntityMixin from "./EntityMixin"
import EntityIcon from "./EntityIcon"
import FileEditor from "@/components/File/EditorModal";
import IconEditor from "@/components/panels/Entities/IconEditor";
import ProcedureEditor from "@/components/Procedure/ProcedureEditorModal"
import Response from "@/components/Action/Response"

export default {
  components: {
    ConfirmDialog,
    EntityIcon,
    FileEditor,
    IconEditor,
    ProcedureEditor,
    Response,
  },
  mixins: [EntityMixin],
  emits: ['delete', 'input', 'loading'],

  props: {
    collapseOnHeaderClick: {
      type: Boolean,
      default: false,
    },

    selected: {
      type: Boolean,
      default: false,
    },
  },

  data: function() {
    return {
      args: {},
      defaultIconClass: 'fas fa-cogs',
      extraArgs: {},
      collapsed_: true,
      infoCollapsed: false,
      lastError: null,
      lastResponse: null,
      newArgName: '',
      newArgValue: '',
      runCollapsed: false,
      showConfirmDelete: false,
      showFileEditor: false,
      showProcedureEditor: false,
    }
  },

  computed: {
    icon() {
      const defaultClass = this.defaultIconClass
      const currentClass = this.value.meta?.icon?.['class']
      let iconClass = currentClass
      if (!currentClass || currentClass === defaultClass) {
        iconClass = this.procedureTypeIconClass || defaultClass
      }

      return {
        ...(this.value.meta?.icon || {}),
        class: iconClass,
      }
    },

    isReadOnly() {
      return this.value.procedure_type !== 'db'
    },

    allArgs() {
      return Object.entries({...this.args, ...this.extraArgs})
        .map(([key, value]) => [key?.trim(), value])
        .filter(
          ([key, value]) => (
            key?.length
            && value != null
            && (
              typeof value !== 'string'
              || value?.trim()?.length > 0
            )
          )
        ).reduce((acc, [key, value]) => {
          acc[key] = value
          return acc
        }, {})
    },

    displayPath() {
      let src = this.value.source
      if (!src?.length) {
        return null
      }

      const configDir = this.$root.configDir
      if (configDir) {
        src = src.replace(new RegExp(`^${configDir}/`), '')
      }

      const line = parseInt(this.value.line)
      if (!isNaN(line)) {
        src += `:${line}`
      }

      return src
    },

    procedureTypeIconClass() {
      if (this.value.procedure_type === 'python')
        return 'fab fa-python'

      if (this.value.procedure_type === 'config')
        return 'fas fa-file'

      if (this.value.procedure_type === 'db')
        return 'fas fa-database'

      return this.defaultIconClass
    },
  },

  methods: {
    async run() {
      this.$emit('loading', true)
      try {
        this.lastResponse = await this.request(`procedure.${this.value.name}`, this.allArgs)
        this.lastError = null
        this.notify({
          text: 'Procedure executed successfully',
          image: {
            icon: 'play',
          }
        })
      } catch (e) {
        this.lastResponse = null
        this.lastError = e
        this.notify({
          text: 'Failed to execute procedure',
          error: true,
          image: {
            icon: 'exclamation-triangle',
          }
        })
      } finally {
        this.$emit('loading', false)
      }
    },

    async remove() {
      this.$emit('loading', true)
      try {
        await this.request('procedures.delete', {name: this.value.name})
        this.$emit('loading', false)
        this.$emit('delete')
        this.notify({
          text: 'Procedure deleted successfully',
          image: {
            icon: 'trash',
          }
        })
      } finally {
        this.$emit('loading', false)
      }
    },

    onHeaderClick(event) {
      if (this.collapseOnHeaderClick) {
        event.stopPropagation()
        this.collapsed_ = !this.collapsed_
      }
    },

    onUpdate(value) {
      if (!this.isReadOnly) {
        this.$emit('input', value)
        this.$nextTick(() => this.$refs.editor?.close())
      }
    },

    updateArg(arg, event) {
      let value = event.target.value
      if (!value?.length) {
        delete this.args[arg]
      }

      try {
        value = JSON.parse(value)
      } catch (e) {
        // Do nothing
      }

      this.args[arg] = value
    },

    updateExtraArgName(oldName, event) {
      let newName = event.target.value?.trim()
      if (newName === oldName) {
        return
      }

      if (newName?.length) {
        if (oldName) {
          this.extraArgs[newName] = this.extraArgs[oldName]
        } else {
          this.extraArgs[newName] = ''
        }
      } else {
        this.focusNewArgName()
      }

      if (oldName) {
        delete this.extraArgs[oldName]
      }
    },

    updateExtraArgValue(arg, event) {
      let value = event.target.value
      if (!value?.length) {
        delete this.extraArgs[arg]
        return
      }

      this.extraArgs[arg] = this.deserializeValue(value)
    },

    addExtraArg() {
      let name = this.newArgName?.trim()
      let value = this.newArgValue
      if (!name?.length || !value?.length) {
        return
      }

      this.extraArgs[name] = this.deserializeValue(value)
      this.newArgName = ''
      this.newArgValue = ''
      this.focusNewArgName()
    },

    deserializeValue(value) {
      try {
        return JSON.parse(value)
      } catch (e) {
        return value
      }
    },

    focusNewArgName() {
      this.$nextTick(() => this.$refs.newArgName.focus())
    },
  },

  watch: {
    collapsed: {
      immediate: true,
      handler(value) {
        this.collapsed_ = value
      },
    },

    selected: {
      immediate: true,
      handler(value) {
        this.collapsed_ = value
      },
    },

    showProcedureEditor(value) {
      if (!value) {
        this.$refs.editor?.reset()
      }
    },
  },

  mounted() {
    this.collapsed_ = !this.selected
  },
}
</script>

<style lang="scss" scoped>
@import "common";

$icon-width: 2em;

.procedure-container {
  .body {
    padding-bottom: 0;
    cursor: default;
  }

  section {
    header {
      background: $tab-bg;
      display: flex;
      align-items: center;
      font-size: 1.1em;
      font-weight: bold;
      margin: 1em -0.5em 0.5em -0.5em;
      padding: 0.25em 1em 0.25em 0.5em;
      border-top: 1px solid $default-shadow-color;
      box-shadow: $border-shadow-bottom;
      cursor: pointer;

      &:hover {
        background: $header-bg;
      }

      &.collapsed {
        margin-bottom: -0.1em;
      }

      .buttons {
        display: flex;
        justify-content: flex-end;
      }

      button.btn {
        background: none;
        border: none;
        color: initial;

        &:hover {
          color: $default-hover-fg;
        }
      }
    }

    &:first-of-type header {
      margin-top: -0.5em;

      &.collapsed {
        margin-bottom: -1em;
      }
    }
  }

  .head {
    &:not(.collapsed) {
      background: $selected-bg;
      border-bottom: 1px solid $default-shadow-color;
    }

    .icon, .collapse-toggler {
      width: $icon-width;
    }

    .label, .value-and-toggler {
      min-width: calc(((100% - (2 * $icon-width)) / 2) - 1em);
      max-width: calc(((100% - (2 * $icon-width)) / 2) - 1em);
    }

    .label {
      margin-left: 1em;
    }

    .value-and-toggler {
      text-align: right;
    }
  }

  form {
    width: 100%;

    .row {
      width: 100%;
      input[type=text] {
        width: 100%;
      }
    }

    .args {
      .arg {
        margin-bottom: 0.25em;
        padding-bottom: 0.25em;
        border-bottom: 1px solid $default-shadow-color;
      }

      .argname {
        font-weight: bold;
      }

      @include until($tablet) {
        .argname {
          width: calc(100% - 2em) !important;
        }

        .argvalue {
          width: 100% !important;
        }
      }

      @include from($tablet) {
        display: flex;
        flex-wrap: wrap;

        .argname {
          width: calc(35% - 2em) !important;
        }

        .argvalue {
          width: 65% !important;
        }
      }
    }

    .run-container {
      display: flex;
      justify-content: center;
      font-size: 1.5em;
      margin-top: 0.5em;

      button {
        padding: 0 1em;
        text-align: center;
        border-radius: 0.5em;
      }
    }
  }

  .info-body {
    .item {
      display: flex;
      padding: 0.5em 0.25em;

      @include until($tablet) {
        border-bottom: 1px solid $default-shadow-color;
      }

      &.delete {
        justify-content: center;

        button {
          width: 100%;
          color: $error-fg;
          padding: 0;

          &:hover {
            color: $default-hover-fg;
          }
        }
      }
    }

    .label {
      font-weight: bold;

      @include until($tablet) {
        width: 100%;
      }

      @include from($tablet) {
        width: 33.3333%;
      }
    }

    .value {
      text-align: right;

      @include until($tablet) {
        width: 100%;
      }

      @include from($tablet) {
        width: 66.6667%;
      }

      a {
        width: 100%;
      }
    }

    .actions {
      @include until($tablet) {
        flex-direction: column;
      }

      .item {
        border-bottom: none;
      }

      button {
        width: 100%;
        height: 2.5em;
        padding: 0;
        border-radius: 1em;

        &:hover {
          color: $default-hover-fg;
        }
      }
    }
  }

  .head-run-btn {
    background: none;
    border: none;
    font-size: 1.25em;

    &:hover {
      background: none;
      color: $default-hover-fg-2;
    }
  }
}
</style>

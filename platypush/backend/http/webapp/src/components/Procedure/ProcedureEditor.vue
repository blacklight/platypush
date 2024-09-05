<template>
  <div class="procedure-editor-container">
    <main>
      <div class="procedure-editor">
        <form class="procedure-edit-form" autocomplete="off" @submit.prevent="executeAction">
          <input type="submit" style="display: none" />

          <div class="name-editor-container" v-if="withName">
            <div class="row item">
              <div class="name">
                <label>
                  <i class="icon fas fa-pen-to-square" />
                  Name
                </label>
              </div>

              <div class="value">
                <input type="text"
                       v-model="newValue.name"
                       ref="nameInput"
                       :disabled="readOnly" />
              </div>
            </div>
          </div>

          <div class="icon-editor-container"
               v-if="Object.keys(newValue?.meta?.icon || {}).length">
            <IconEditor :entity="newValue"
                        @input="onIconChange"
                        @change="onIconChange" />
          </div>

          <div class="args-editor-container" v-if="showArgs">
            <h3>
              <i class="icon fas fa-code" />&nbsp;
              Arguments
            </h3>

            <div class="args" ref="args">
              <div class="row item" v-for="(arg, index) in newValue.args" :key="index">
                <input type="text"
                       placeholder="Argument Name"
                       :value="arg"
                       :disabled="readOnly"
                       @input="onArgInput($event.target.value?.trim(), index)"
                       @blur="onArgEdit(arg, index)" />
              </div>

              <div class="row item new-arg" v-if="!readOnly">
                <input type="text"
                       placeholder="New Argument"
                       ref="newArgInput" 
                       v-model="newArg"
                       @blur="onNewArg" />
              </div>
            </div>
          </div>

          <div class="actions-container">
            <h3 v-if="showArgs">
              <i class="icon fas fa-play" />&nbsp;
              Actions
            </h3>

            <ActionsList :value="newValue.actions"
                         :read-only="readOnly"
                         @input="newValue.actions = $event" />
          </div>

          <!-- Structured response container -->
          <div class="response-container" v-if="response || error">
            <Response :response="response" :error="error" />
          </div>
        </form>
      </div>

      <div class="args-modal-container" ref="argsModalContainer" v-if="showArgsModal">
        <Modal title="Run Arguments"
               :visible="true"
               ref="argsModal"
               @close="onRunArgsModalClose">
          <form class="args" @submit.prevent="executeWithArgs">
            <div class="row item" v-for="value, arg in runArgs" :key="arg">
              <span class="arg-name">
                <span v-if="newValue.args?.includes(arg)">
                  {{ arg }}
                </span>

                <span v-else>
                  <input type="text"
                         placeholder="New Argument"
                         :value="arg"
                         @input="onEditRunArgName($event, arg)">
                </span>

                <span class="mobile">
                  &nbsp;=&nbsp;
                </span>
              </span>

              <span class="arg-value">
                <span class="from tablet">
                  &nbsp;=&nbsp;
                </span>

                <input type="text"
                       placeholder="Argument Value"
                       :ref="`run-arg-value-${arg}`"
                       v-model="runArgs[arg]" />
              </span>
            </div>

            <div class="row item new-arg">
              <span class="arg-name">
                <input type="text"
                       placeholder="New Argument"
                       ref="newRunArgName"
                       v-model="newRunArg[0]"
                       @blur="onNewRunArgName" />

                <span class="mobile">
                  &nbsp;=&nbsp;
                </span>
              </span>
              <span class="arg-value">
                <span class="from tablet">
                  &nbsp;=&nbsp;
                </span>

                <input type="text"
                       placeholder="Argument Value"
                       v-model="newRunArg[1]" />
              </span>
            </div>

            <input type="submit" style="display: none" />
            <FloatingButton icon-class="fa fa-play"
                            title="Run Procedure"
                            :disabled="newValue.actions?.length === 0 || running"
                            @click="executeWithArgs" />
          </form>
        </Modal>
      </div>

      <div class="confirm-dialog-container">
        <ConfirmDialog ref="confirmClose" @input="forceClose">
          This procedure has unsaved changes. Are you sure you want to close it?
        </ConfirmDialog>
      </div>

      <div class="confirm-dialog-container">
        <ConfirmDialog ref="confirmOverwrite" @input="forceSave">
          A procedure with the same name already exists. Do you want to overwrite it?
        </ConfirmDialog>
      </div>

      <div class="spacer" />

      <div class="floating-buttons">
        <div class="buttons left">
          <FloatingButtons direction="row">
              <FloatingButton icon-class="fa fa-code"
                              left glow
                              title="Export to YAML"
                              @click="showYAML = true" />
              <FloatingButton icon-class="fa fa-copy"
                              left glow
                              title="Duplicate Procedure"
                              @click="duplicate"
                              v-if="newValue.name?.length && newValue.actions?.length" />
          </FloatingButtons>
        </div>

        <div class="buttons right">
          <FloatingButtons direction="row">
              <FloatingButton icon-class="fa fa-save"
                              right glow
                              title="Save Procedure"
                              :disabled="!hasChanges"
                              @click="save"
                              v-if="showSave" />
              <FloatingButton icon-class="fa fa-play"
                              right glow
                              title="Run Procedure"
                              :disabled="newValue.actions?.length === 0 || running"
                              @click="executeAction" />
          </FloatingButtons>
        </div>
      </div>
    </main>

    <div class="duplicate-editor-container" v-if="duplicateValue != null">
      <Modal title="Duplicate Procedure"
             ref="duplicateModal"
             :visible="true"
             :before-close="(() => $refs.duplicateEditor?.checkCanClose())"
             @close="duplicateValue = null">
        <ProcedureEditor :value="duplicateValue"
                         :with-name="true"
                         :with-save="true"
                         :modal="() => $refs.duplicateModal"
                         ref="duplicateEditor"
                         @input="duplicateValue = null" />
      </Modal>
    </div>

    <div class="dump-modal-container" v-if="showYAML">
      <Modal title="Procedure Dump"
             :visible="true"
             @close="showYAML = false">
        <ProcedureDump :procedure="newValue" />
      </Modal>
    </div>
  </div>
</template>

<script>
import ActionsList from "@/components/Action/ActionsList"
import ConfirmDialog from "@/components/elements/ConfirmDialog";
import FloatingButton from "@/components/elements/FloatingButton";
import FloatingButtons from "@/components/elements/FloatingButtons";
import IconEditor from "@/components/panels/Entities/IconEditor";
import Modal from "@/components/Modal";
import ProcedureDump from "./ProcedureDump";
import Response from "@/components/Action/Response"
import Utils from "@/Utils"

export default {
  mixins: [Utils],
  emits: ['input'],
  components: {
    ActionsList,
    ConfirmDialog,
    FloatingButton,
    FloatingButtons,
    IconEditor,
    Modal,
    ProcedureDump,
    Response,
  },

  props: {
    withName: {
      type: Boolean,
      default: false,
    },

    withSave: {
      type: Boolean,
      default: false,
    },

    value: {
      type: Object,
      default: () => ({
        name: undefined,
        actions: [],
      }),
    },

    readOnly: {
      type: Boolean,
      default: false,
    },

    modal: {
      type: [Object, Function],
    },
  },

  data() {
    return {
      confirmOverwrite: false,
      duplicateValue: null,
      error: undefined,
      loading: false,
      newAction: {},
      newArg: null,
      newRunArg: [null, null],
      newValue: {},
      response: undefined,
      running: false,
      runArgs: {},
      shouldForceClose: false,
      showArgsModal: false,
      showYAML: false,
    }
  },

  computed: {
    floatingButtons() {
      return this.$el.querySelector('.floating-btns')
    },

    hasChanges() {
      if (!this.newValue?.name?.length)
        return false

      if (!this.newValue?.actions?.length)
        return false

      return JSON.stringify(this.value) !== JSON.stringify(this.newValue)
    },

    modal_() {
      if (this.readOnly)
        return null

      return typeof this.modal === 'function' ? this.modal() : this.modal
    },

    shouldConfirmClose() {
      return this.hasChanges && !this.readOnly && this.withSave && !this.shouldForceClose
    },

    showArgs() {
      return !this.readOnly || this.newValue.args?.length
    },

    showSave() {
      return this.withSave && !this.readOnly
    },
  },

  methods: {
    async save() {
      if (!this.hasChanges)
        return

      this.loading = true
      try {
        const overwriteOk = await this.overwriteOk()
        if (!overwriteOk)
          return

        const actions = this.newValue.actions.map((action) => {
          const a = {...action}
          if ('name' in a) {
            a.action = a.name
            delete a.name
          }

          return a
        })

        const args = {...this.newValue, actions}
        if (this.value?.name?.length && this.value.name !== this.newValue.name) {
          args.old_name = this.value.name
        }

        await this.request('procedures.save', args)
        this.$emit('input', this.newValue)
        this.notify({
          text: 'Procedure saved successfully',
          image: {
            icon: 'check',
          }
        })
      } finally {
        this.loading = false
      }
    },

    async forceSave() {
      this.confirmOverwrite = true
      await this.save()
    },

    async overwriteOk() {
      if (this.confirmOverwrite) {
        this.confirmOverwrite = false
        return true
      }

      const procedures = await this.request('procedures.status', {publish: false})
      if (
        this.value.name?.length &&
        this.value.name !== this.newValue.name &&
        procedures[this.newValue.name]
      ) {
        this.$refs.confirmOverwrite?.open()
        return false
      }

      return true
    },

    onResponse(response) {
      this.response = (
        typeof response === 'string' ? response : JSON.stringify(response, null, 2)
      ).trim()

      this.error = undefined
    },

    onError(error) {
      if (error.message)
        error = error.message

      this.response = undefined
      this.error = error
    },

    onDone() {
      this.running = false
      this.runArgs = {}
    },

    async executeAction() {
      if (!this.newValue.actions?.length) {
        this.notify({
          text: 'No actions to execute',
          warning: true,
          image: {
            icon: 'exclamation-triangle',
          }
        })

        return
      }

      if (this.newValue.args?.length && !Object.keys(this.runArgs).length) {
        this.showArgsModal = true
        return
      }

      this.running = true
      try {
        const procedure = {
          actions: this.newValue.actions.map((action) => {
            const a = {...action}
            if ('name' in a) {
              a.action = a.name
              delete a.name
            }

            return a
          }),

          args: this.runArgs,
        }

        const response = await this.request('procedures.exec', {procedure})
        this.onResponse(response)
      } catch (e) {
        console.error(e)
        this.onError(e)
      } finally {
        this.onDone()
      }
    },

    async executeWithArgs() {
      this.$refs.argsModal?.close()
      Object.entries(this.runArgs).forEach(([arg, value]) => {
        if (!value?.length)
          this.runArgs[arg] = null

        try {
          this.runArgs[arg] = JSON.parse(value)
        } catch (e) {
          // ignore
        }
      })

      await this.executeAction()
    },

    duplicate() {
      const name = `${this.newValue.name || ''}__copy`
      this.duplicateValue = {
        ...this.newValue,
        ...{
          meta: {
            ...(this.newValue.meta || {}),
            icon: {...(this.newValue.meta?.icon || {})},
          }
        },
        id: null,
        external_id: name,
        name: name,
      }
    },

    editAction(action, index) {
      this.newValue.actions[index] = action
    },

    addAction(action) {
      this.newValue.actions.push(action)
    },

    deleteAction(index) {
      this.newValue.actions.splice(index, 1)
    },

    onArgInput(arg, index) {
      this.newValue.args[index] = arg
    },

    onArgEdit(arg, index) {
      arg = arg?.trim()
      const isDuplicate = !!(
        this.newValue.args?.filter(
          (a, i) => a === arg && i !== index
        ).length
      )

      if (!arg?.length || isDuplicate) {
        this.newValue.args.splice(index, 1)

        if (index === this.newValue.args.length) {
          setTimeout(() => this.$refs.newArgInput?.focus(), 50)
        } else {
          const nextInput = this.$refs.args.children[index]?.querySelector('input[type=text]')
          setTimeout(() => {
            nextInput?.focus()
            nextInput?.select()
          }, 50)
        }
      }
    },

    onNewArg(event) {
      const value = event.target.value?.trim()
      if (!value?.length) {
        return
      }

      if (!this.newValue.args) {
        this.newValue.args = []
      }

      if (!this.newValue.args.includes(value)) {
        this.newValue.args.push(value)
      }

      this.newArg = null
      setTimeout(() => this.$refs.newArgInput?.focus(), 50)
    },

    onNewRunArgName() {
      const arg = this.newRunArg[0]?.trim()
      const value = this.newRunArg[1]?.trim()
      if (!arg?.length) {
        return
      }

      this.runArgs[arg] = value
      this.newRunArg = [null, null]
      this.$nextTick(() => this.$refs[`run-arg-value-${arg}`]?.[0]?.focus())
    },

    onEditRunArgName(event, arg) {
      const newArg = event.target.value?.trim()
      if (newArg === arg) {
        return
      }

      if (newArg?.length) {
        this.runArgs[newArg] = this.runArgs[arg]
      }

      delete this.runArgs[arg]
      this.$nextTick(
        () => this.$el.querySelector(`.args-modal-container .args input[type=text][value="${newArg}"]`)?.focus()
      )
    },

    onIconChange(icon) {
      this.newValue.meta.icon = icon
    },

    onRunArgsModalClose() {
      this.showArgsModal = false
      this.$nextTick(() => {
        this.runArgs = {}
      })
    },

    checkCanClose() {
      if (!this.shouldConfirmClose)
        return true

      this.$refs.confirmClose?.open()
      return false
    },

    forceClose() {
      this.shouldForceClose = true
      this.$nextTick(() => {
        if (!this.modal_)
          return

        let modal = this.modal_
        if (typeof modal === 'function') {
          modal = modal()
        }

        try {
          modal?.close()
        } catch (e) {
          console.warn('Failed to close modal', e)
        }

        this.reset()
      })
    },

    beforeUnload(e) {
      if (this.shouldConfirmClose) {
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
      this.removeBeforeUnload()
    },

    syncValue() {
      if (!this.value)
        return

      this.newValue = {
        ...this.value,
        actions: this.value.actions?.map(a => ({...a})),
        args: [...(this.value?.args || [])],
        meta: {...(this.value?.meta || {})},
      }
    },
  },

  watch: {
    value: {
      immediate: true,
      deep: true,
      handler() {
        this.syncValue()
      },
    },

    newValue: {
      deep: true,
      handler(value) {
        if (this.withSave)
          return

        this.$emit('input', value)
      },
    },

    showArgsModal(value) {
      if (value) {
        this.runArgs = this.newValue.args?.reduce((acc, arg) => {
          acc[arg] = null
          return acc
        }, {})

        this.$nextTick(() => {
          this.$el.querySelector('.args-modal-container .args input[type=text]')?.focus()
        })
      }
    },
  },

  mounted() {
    this.addBeforeUnload()
    this.syncValue()
    this.$nextTick(() => {
      if (this.withName)
        this.$refs.nameInput?.focus()
    })
  },

  unmouted() {
    this.reset()
  },
}
</script>

<style lang="scss" scoped>
$floating-btns-height: 3em;

.procedure-editor-container {
  display: flex;
  flex-direction: column;
  padding-top: 0.75em;
  position: relative;
  max-height: 75vh;

  main {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow: auto;
  }

  .procedure-editor {
    width: 100%;
    height: calc(100% - #{$floating-btns-height});
    overflow: auto;
    padding: 0 1em;

    .procedure-edit-form {
      padding-bottom: calc(#{$floating-btns-height} + 1em);
    }
  }

  h3 {
    font-size: 1.2em;
  }

  .name-editor-container {
    .row {
      display: flex;
      border-bottom: 1px solid $default-shadow-color;
      align-items: center;
      justify-content: space-between;
      padding-bottom: 0.5em;
      margin-bottom: 0.5em;

      @include until($tablet) {
        flex-direction: column;
        align-items: flex-start;
      }

      @include from($tablet) {
        flex-direction: row;
      }

      .name {
        margin-right: 0.5em;
      }

      .value {
        flex: 1;

        @include until($tablet) {
          width: 100%;
        }

        input {
          width: 100%;
        }
      }
    }
  }

  .icon-editor-container {
    border-bottom: 1px solid $default-shadow-color;
    margin-bottom: 0.5em;
  }

  .spacer {
    width: 100%;
    height: calc(#{$floating-btns-height} + 1em);
    flex-grow: 1;
  }

  .args-editor-container {
    .args {
      margin-bottom: 1em;

      .item {
        padding-bottom: 0.5em;
      }
    }
  }

  :deep(.args-modal-container) {
    .modal-container .modal {
      width: 50em;

      .body {
        padding: 1em;
      }
    }

    .args {
      position: relative;
      padding-bottom: calc(#{$floating-btn-size} + 2em);

      .row {
        display: flex;
        align-items: center;
        margin-bottom: 0.5em;

        @include until($tablet) {
          flex-direction: column;
          align-items: flex-start;
          border-bottom: 1px solid $default-shadow-color;
          padding-bottom: 0.5em;
        }

        .arg-name {
          @extend .col-s-12;
          @extend .col-m-5;
          font-weight: bold;

          input {
            width: 100%;

            @include until($tablet) {
              width: calc(100% - 2em);
            }
          }
        }

        .arg-value {
          @extend .col-s-12;
          @extend .col-m-7;
          flex: 1;

          input[type=text] {
            width: 95%;
          }
        }
      }
    }
  }

  :deep(.floating-buttons) {
    width: 100%;
    height: $floating-btns-height;
    position: absolute;
    bottom: 0;
    left: 0;
    background: $default-bg-5;
    box-shadow: $border-shadow-top;
    display: flex;
    justify-content: space-between;

    .buttons {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      padding: 0 1em;
      position: relative;
    }
  }

  :deep(.dump-modal-container) {
    .body {
      max-width: 47em;
    }
  }
}
</style>

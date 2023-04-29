<template>
  <Modal :visible="visible" title="Set Variable" ref="modal"
      @open="onOpen" @close="$emit('close', $event)">
    <div class="variable-modal-container">
      <form @submit.prevent="setValue">
        <div class="row">
          <div class="col-s-12 col-m-4 label">
            <label for="name">Variable Name</label>
          </div>
          <div class="col-s-12 col-m-8 value">
            <input type="text" id="variable-name" v-model="varName"
              placeholder="Variable Name" :disabled="loading" ref="varName" />
          </div>
        </div>

        <div class="row">
          <div class="col-s-12 col-m-4 label">
            <label for="name">Variable Value</label>
          </div>
          <div class="col-s-12 col-m-8 value">
            <input type="text" id="variable-value" v-model="varValue" ref="varValue"
              placeholder="Variable Value" :disabled="loading" />
          </div>
        </div>

        <div class="row button-container">
          <button type="submit" title="Set" :disabled="loading">
            <i class="fas fa-check" />
          </button>
        </div>
      </form>
    </div>
  </Modal>
</template>

<script>
import Modal from "@/components/Modal";
import Utils from "@/Utils";

export default {
  name: "VariableModal",
  components: {Modal},
  mixins: [Utils],
  emits: ['close'],
  props: {
    visible: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      loading: false,
      varName: null,
      varValue: null,
    };
  },

  methods: {
    async clearValue() {
      this.loading = true
      try {
        await this.request('variable.unset', {name: this.varName.trim()})
      } finally {
        this.loading = false
      }
    },

    async setValue() {
      const varName = this.varName.trim()
      if (!varName?.length) {
        this.notifyWarning('No variable name has been specified')
      }

      const value = this.varValue
      if (!value?.length) {
        await this.clearValue()
      } else {
        this.loading = true
        try {
          const args = {}
          args[varName] = value
          await this.request('variable.set', args)
        } finally {
          this.loading = false
        }
      }

      this.$refs.varName.value = ''
      this.$refs.varValue.value = ''
      this.$refs.modal.close()
    },

    onOpen() {
      this.$nextTick(() => {
        this.$refs.varName.focus()
      })
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.variable-modal-container {
  form {
    padding: 1em 0;

    label {
      font-weight: bold;
    }

    .row {
      padding: 0.25em 1em;
      display: flex;
      align-items: center;

      @include until($tablet) {
        flex-direction: column;
      }

      input[type=text] {
        width: 100%;
      }
    }

    .button-container {
      display: flex;
      justify-content: center;
      margin-top: 0.5em;
      margin-bottom: -0.75em;
      padding-top: 0.5em;
      border-top: 1px solid $border-color-1;

      button {
        min-width: 10em;
        background: none;
        border-radius: 1.5em;

        &:hover {
          background: $hover-bg;
        }
      }
    }

    @include from($tablet) {
      .value {
        text-align: right;
      }
    }
  }
}
</style>

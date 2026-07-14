<template>
  <div class="entity variable-container">
    <div class="head" :class="{collapsed: collapsed}">
      <div class="icon">
        <EntityIcon :entity="value" :loading="loading" :error="error" />
      </div>

      <div class="label">
        <div class="name" v-text="value.name" />
      </div>

      <div class="value-and-toggler" @click.stop="collapsed = !collapsed">
        <div class="value" :class="{truncated: collapsed}" v-text="value.value" />
        <div class="collapse-toggler" @click.stop="collapsed = !collapsed">
          <i class="fas" :class="{'fa-chevron-down': collapsed, 'fa-chevron-up': !collapsed}" />
        </div>
      </div>
    </div>

    <div class="body" v-if="!collapsed" @click.stop="prevent">
      <div class="row">
        <form @submit.prevent="setValue">
          <div class="row">
            <div class="col-9">
              <textarea v-model="value_" placeholder="Variable value" :disabled="loading" ref="text" rows="1" />
            </div>
            <div class="col-3 pull-right">
              <button type="button" title="Delete Variable" @click.stop="showDeleteConfirm" :disabled="loading">
                <i class="fas fa-trash" />
              </button>
              <button type="button" title="Clear Value" @click.stop="clearValue" :disabled="loading">
                <i class="fas fa-eraser" />
              </button>
              <button type="submit" title="Save" :disabled="loading">
                <i class="fas fa-check" />
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <ConfirmDialog ref="deleteConfirmDialog" @input="deleteVariable">
      Are you sure you want to delete this variable?<br/><br/>
      <b>{{ value.name }}</b>
    </ConfirmDialog>
  </div>
</template>

<script>
import ConfirmDialog from "@/components/elements/ConfirmDialog"
import EntityMixin from "./EntityMixin"
import EntityIcon from "./EntityIcon"

export default {
  name: 'Variable',
  components: {ConfirmDialog, EntityIcon},
  mixins: [EntityMixin],
  emits: ['loading'],
  data: function() {
    return {
      collapsed: true,
      value_: null,
    }
  },

  computed: {
    isCollapsed() {
      return this.collapsed
    },
  },

  methods: {
    autoResizeTextarea() {
      const textarea = this.$refs.text
      if (!textarea)
        return

      textarea.style.height = 'auto'
      textarea.style.height = Math.min(textarea.scrollHeight, 300) + 'px'
    },

    showDeleteConfirm() {
      this.$refs.deleteConfirmDialog.show()
    },

    async deleteVariable() {
      this.$emit('loading', true)
      try {
        await this.request('entities.delete', [this.value.id])
        this.$refs.deleteConfirmDialog?.close()
      } finally {
        this.$emit('loading', false)
      }
    },

    async clearValue() {
      this.$emit('loading', true)
      try {
        await this.request('variable.unset', {name: this.value.name})
      } finally {
        this.$emit('loading', false)
      }
    },

    async setValue() {
      const value = this.value_
      if (!value?.length)
        return await this.clearValue()

      this.$emit('loading', true)
      try {
        const args = {}
        args[this.value.name] = value
        await this.request('variable.set', args)
      } finally {
        this.$emit('loading', false)
      }
    },
  },

  mounted() {
    this.value_ = this.value.value
    this.$watch(() => this.value.value, (newValue) => {
      this.value_ = newValue
      this.$nextTick(() => this.autoResizeTextarea())
    })

    this.$watch(() => this.value_, () => {
      this.$nextTick(() => this.autoResizeTextarea())
    })

    this.$watch(() => this.collapsed, (newVal) => {
      if (!newVal) {
        this.$nextTick(() => this.autoResizeTextarea())
      }
    })
  },
}
</script>

<style lang="scss" scoped>
@import "common";

$icon-width: 2em;

.variable-container {
  .head {
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

      .value {
        &.truncated {
          max-height: 2.4em;
          overflow: hidden;
          text-overflow: ellipsis;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          word-break: break-word;
        }
      }
    }
  }

  form {
    width: 100%;

    .row {
      width: 100%;
      
      input[type=text], textarea {
        width: 100%;
      }

      textarea {
        min-height: 2.5em;
        max-height: 300px;
        resize: vertical;
        overflow-y: auto;
        font-family: inherit;
        padding: 0.5em;
      }

      .pull-right {
        display: flex;
        justify-content: flex-end;
        gap: 0.5em;
      }
    }
  }
}
</style>

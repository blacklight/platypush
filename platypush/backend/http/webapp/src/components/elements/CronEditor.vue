<template>
  <div class="cron-editor-container">
    <div class="input-grid" :class="{error: error != null}">
      <label class="item" :class="{selected: selectedItem === i}" v-for="(label, i) in labels" :key="i">
        <div class="col-s-12 col-m-4" v-text="label" />
        <div class="col-s-12 col-m-8">
          <input type="text" v-model="cronExpr[i]"
                 @keydown="validate"
                 @input="updateCronExpr(i, $event.target.value)"
                 @focus="selectedItem = i"
                 @blur="selectedItem = null" />
        </div>
      </label>
    </div>

    <div class="cron-description-container">
      <div class="error" v-if="error" v-text="error" />
      <div class="cron-description" v-else>
        <CopyButton :text="cronString" />
        <div class="cron-string" v-text="cronString" />
        <div class="cron-next-run" v-if="!error">
          Runs: <span class="cron-text" v-text="cronDescription" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import cronstrue from 'cronstrue'
import CopyButton from "@/components/elements/CopyButton"

export default {
  emits: ['input'],
  components: {
    CopyButton,
  },
  props: {
    value: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      cronExpr: this.value.split(/\s+/),
      cronDescription: null,
      error: null,
      selectedItem: null,
      cronRegex: new RegExp('^[0-9*/,-]*$'),
      labels: [
        'Minute',
        'Hour',
        'Day of Month',
        'Month',
        'Day of Week',
      ],
    }
  },

  computed: {
    cronString() {
      return this.cronExpr.map((v) => v.trim()).join(' ')
    },
  },

  watch: {
    cronExpr: {
      handler(newValue, oldValue) {
        newValue.forEach((v, i) => {
          v = v.trim()
          if (!v.match(this.cronRegex)) {
            this.cronExpr[i] = oldValue[i]
          } else {
            this.cronExpr[i] = v
          }
        })
      },
      deep: true,
    },
  },

  methods: {
    validate(e) {
      const key = e.key

      if (
        [
          'Enter',
          'Escape',
          'Tab',
          'ArrowLeft',
          'ArrowRight',
          'ArrowUp',
          'ArrowDown',
          'Backspace',
          'Delete',
          'Home',
          'End'
        ].includes(key) ||
        e.ctrlKey ||
        e.metaKey
      ) {
        return
      }

      if (key.match(this.cronRegex)) {
        return
      }

      e.preventDefault()
    },

    updateCronDescription() {
      try {
        const text = cronstrue.toString(this.cronString)
        this.error = null
        this.cronDescription = text
      } catch (e) {
        this.error = `Invalid cron expression: ${e}`
        this.cronDescription = null
      }
    },

    updateCronExpr(index, value) {
      this.cronExpr[index] = value
      this.updateCronDescription()
      if (!this.error)
        this.$emit('input', this.cronString)
    },
  },

  mounted() {
    this.updateCronDescription()
  },
}
</script>

<style lang="scss" scoped>
.cron-editor-container {
  display: flex;
  flex-direction: column;

  .input-grid {
    label {
      display: flex;
      align-items: center;
      font-weight: bold;
      border: 1px solid transparent;
      border-radius: 1em;
      padding: 0.25em;

      &.selected {
        border: 1px solid $selected-fg;
      }
    }

    input[type="text"] {
      width: 100%;
    }
  }

  .error {
    color: $error-fg;

    label {
      input[type="text"] {
        border-color: $error-fg;
      }
    }
  }

  .cron-description-container {
    margin-top: 0.5em;
    padding: 0.5em;
    font-size: 0.9em;
    font-weight: bold;
    background: $code-dark-bg;
    color: $code-dark-fg;
    border-radius: 1em;
    border: $default-border-3;

    .cron-description {
      display: flex;
      flex-direction: column;
      justify-content: center;
      position: relative;
    }

    .cron-string {
      font-family: monospace;
      font-size: 1.1em;
    }

    .cron-text {
      font-weight: normal;
      font-style: italic;
    }
  }
}
</style>

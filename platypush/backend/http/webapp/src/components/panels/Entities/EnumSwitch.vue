<template>
  <div class="entity switch-container">
    <div class="head" :class="{collapsed: collapsed}">
      <div class="icon">
        <EntityIcon :entity="value" :loading="loading" :error="error" />
      </div>

      <div class="label">
        <div class="name" v-text="value.name" />
      </div>

      <div class="value-container">
        <span class="value"
          v-text="value.values[value.value] || value.value"
          v-if="value?.value != null" />
        <button @click.stop="collapsed = !collapsed" v-if="hasValues">
          <i class="fas"
            :class="{'fa-angle-up': !collapsed, 'fa-angle-down': collapsed}" />
        </button>
      </div>
    </div>

    <div class="body" v-if="!collapsed" @click.stop="prevent">
      <div class="row">
        <div class="input">
          <select @input="setValue" ref="values" :disabled="loading">
            <option value="" v-if="value.is_write_only" selected>--</option>
            <option
              :value="value_id"
              :selected="value_id == value.value"
              :key="value_id"
              v-for="text, value_id in displayValues"
              v-text="text"
            />
          </select>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import EntityMixin from "./EntityMixin"
import EntityIcon from "./EntityIcon"

export default {
  name: 'EnumSwitch',
  components: {EntityIcon},
  mixins: [EntityMixin],

  computed: {
    hasValues() {
      return !!Object.values(this?.value?.values || {}).length
    },

    displayValues() {
      if (this.value?.values instanceof Array)
        return this.value.values.reduce((obj, value) => {
          obj[value] = value
          return obj
        }, {})

      return this.value?.values || {}
    }
  },

  methods: {
    prevent(event) {
      event.stopPropagation()
      return false
    },

    async setValue(event) {
      if (!event.target.value?.length)
        return

      this.$emit('loading', true)
      if (this.value.is_write_only) {
        const self = this;
        setTimeout(() => {
            self.$refs.values.value = ''
        }, 1000)
      }

      try {
        await this.request('entities.execute', {
          id: this.value.id,
          action: 'set',
          value: event.target.value,
        })
      } finally {
        this.$emit('loading', false)
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.switch-container {
  .head {
    .value-container {
      button {
        margin-right: 0.5em;
      }
    }
  }

  .body {
    padding: 1em !important;
    display: flex;

    .row {
      width: 100%;
      display: flex;
      text-align: center;

      .icon {
        width: 2em;
        text-align: center;
      }

      .input {
        width: 100%;

        select {
          width: 100%;
        }
      }
    }
  }
}
</style>

<template>
  <div class="entity variable-container" v-if="value.value != null">
    <div class="head" :class="{collapsed: collapsed}">
      <div class="icon">
        <EntityIcon :entity="value" :loading="loading" :error="error" />
      </div>

      <div class="label">
        <div class="name" v-text="value.name" />
      </div>

      <div class="value-container" @click.stop="collapsed = !collapsed">
        <span class="value" v-text="value.value" v-if="value?.value != null" />
      </div>

      <div class="collapse-toggler" @click.stop="collapsed = !collapsed">
        <i class="fas" :class="{'fa-chevron-down': collapsed, 'fa-chevron-up': !collapsed}" />
      </div>
    </div>

    <div class="body" v-if="!collapsed" @click.stop="prevent">
      <div class="row">
        <form @submit.prevent="setValue">
          <div class="row">
            <div class="col-9">
              <input type="text" :value="value.value" placeholder="Variable value" :disabled="loading" ref="text" />
            </div>
            <div class="col-3 pull-right">
              <button type="button" title="Clear" @click.stop="clearValue" :disabled="loading">
                <i class="fas fa-trash" />
              </button>
              <button type="submit" title="Edit" :disabled="loading">
                <i class="fas fa-check" />
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import EntityMixin from "./EntityMixin"
import EntityIcon from "./EntityIcon"

export default {
  name: 'Variable',
  components: {EntityIcon},
  mixins: [EntityMixin],
  data: function() {
    return {
      collapsed: true,
    }
  },

  computed: {
    isCollapsed() {
      return this.collapsed
    },
  },

  methods: {
    async clearValue() {
      this.$emit('loading', true)
      try {
        await this.request('variable.unset', {name: this.value.name})
      } finally {
        this.$emit('loading', false)
      }
    },

    async setValue() {
      const value = this.$refs.text.value
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
}
</script>

<style lang="scss" scoped>
@import "common";

$icon-width: 2em;

.variable-container {
  .head {
    .icon, .collapse-toggler {
      width: $icon-width;
      margin-right: 0;
    }

    .label, .value-container {
      max-width: calc(((100% - (2 * $icon-width)) / 2) - 0.75em);
    }

    .value-container {
      margin-left: 0.5em;
      text-align: right;
    }

    .collapse-toggler {
      margin-right: 1em;
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
  }
}
</style>

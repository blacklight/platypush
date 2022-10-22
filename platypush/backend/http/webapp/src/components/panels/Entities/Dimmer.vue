<template>
  <div class="entity dimmer-container">
    <div class="head" :class="{expanded: expanded}">
      <div class="col-1 icon">
        <EntityIcon
          :icon="this.value.meta?.icon || {}"
          :loading="loading"
          :error="error" />
      </div>

      <div class="col-s-8 col-m-9 label">
        <div class="name" v-text="value.name" />
      </div>

      <div class="col-s-3 col-m-2 buttons pull-right">
        <button @click.stop="expanded = !expanded">
          <i class="fas"
            :class="{'fa-angle-up': expanded, 'fa-angle-down': !expanded}" />
        </button>
        <span class="value-percent"
          v-text="valuePercent.toFixed(0) + '%'"
          v-if="valuePercent != null" />
      </div>
    </div>

    <div class="body" v-if="expanded" @click.stop="prevent">
      <div class="row">
        <div class="input">
          <Slider :range="[value.min, value.max]"
            :value="value.value" @input="setValue" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Slider from "@/components/elements/Slider"
import EntityMixin from "./EntityMixin"
import EntityIcon from "./EntityIcon"

export default {
  name: 'Dimmer',
  components: {Slider, EntityIcon},
  mixins: [EntityMixin],

  data() {
    return {
      expanded: false,
    }
  },

  computed: {
    valuePercent() {
      if (this.value?.is_write_only || this.value?.value == null)
        return null

      const min = this.value.min || 0
      const max = this.value.max || 100
      return (100 * this.value.value) / (max - min)
    }
  },

  methods: {
    prevent(event) {
      event.stopPropagation()
      return false
    },

    async setValue(event) {
      this.$emit('loading', true)

      try {
        await this.request('entities.execute', {
          id: this.value.id,
          action: 'set_value',
          data: +event.target.value,
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

.dimmer-container {
  .head {
    .buttons {
      button {
        margin-right: 0.5em;
      }
    }

    .value-percent {
      font-size: 1.1em;
      font-weight: bold;
      opacity: 0.7;
    }
  }

  .body {
    .row {
      display: flex;

      .icon {
        width: 2em;
        text-align: center;
      }

      .input {
        width: calc(100% - 2em);

        :deep(.slider) {
          margin-top: 0.5em;
        }
      }
    }
  }
}
</style>

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
          v-text="parsedValue"
          v-if="parsedValue != null" />
      </div>
    </div>

    <div class="body" v-if="expanded" @click.stop="prevent">
      <div class="row">
        <div class="input" v-if="value?.min != null && value?.max != null">
          <div class="col-10">
            <Slider :range="[value.min, value.max]" with-range
              :value="value.value" @input="setValue" />
          </div>
          <div class="col-2 value">
            <input type="number" :value="value.value" @change="setValue">
          </div>
        </div>
        <div class="input" v-else>
          <div class="col-12 value">
            <input type="number" :value="value.value" @change="setValue">
          </div>
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
    parsedValue() {
      if (this.value?.is_write_only || this.value?.value == null)
        return null

      return this.value.value
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
        width: calc(100% - 1em);
        display: flex;
        align-items: center;

        :deep(.slider) {
          margin-top: 0.5em;
        }

        .value {
          input {
            width: 100%;
          }
        }
      }
    }
  }
}
</style>

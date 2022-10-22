<template>
  <div class="entity switch-container">
    <div class="head">
      <div class="col-1 icon">
        <EntityIcon :icon="value.meta?.icon || {}"
          :loading="loading" :error="error" />
      </div>

      <div class="col-9 label">
        <div class="name" v-text="value.name" />
      </div>

      <div class="col-2 switch pull-right">
        <ToggleSwitch
          :value="value.is_write_only ? false : value.state"
          :disabled="loading || value.is_read_only" 
          @input="toggle"
          @click.stop />
      </div>
    </div>
  </div>
</template>

<script>
import ToggleSwitch from "@/components/elements/ToggleSwitch"
import EntityIcon from "./EntityIcon"
import EntityMixin from "./EntityMixin"

export default {
  name: 'Switch',
  components: {ToggleSwitch, EntityIcon},
  mixins: [EntityMixin],

  methods: {
    async toggle(event) {
      event.stopPropagation()
      this.$emit('loading', true)

      try {
        await this.request('entities.execute', {
          id: this.value.id,
          action: 'toggle',
        })

        if (this.value.is_write_only) {
          // Show a quick on/off animation for write-only switches
          const self = this
          self.value.state = true
          setTimeout(() => self.value.state = false, 250)
        }
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
  .switch {
    direction: rtl;
  }
}
</style>

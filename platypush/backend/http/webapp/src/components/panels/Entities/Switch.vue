<template>
  <div class="switch-container">
    <div class="col-10 label">
      <div class="name" v-text="value.name" />
    </div>

    <div class="col-2 switch pull-right">
      <ToggleSwitch :value="value.state" @input="toggle"
        :disabled="loading" />
    </div>
  </div>
</template>

<script>
import ToggleSwitch from "@/components/elements/ToggleSwitch"
import Utils from "@/Utils"

export default {
  name: 'Switch',
  components: {ToggleSwitch},
  emits: ['input'],
  mixins: [Utils],
  props: {
    value: {
      type: Object,
      required: true,
    },

    loading: {
      type: Boolean,
      default: false,
    },
  },

  methods: {
    async toggle(event) {
      event.stopPropagation()
      this.$emit('loading', true)

      try {
        await this.request('entities.execute', {
          id: this.value.id,
          action: 'toggle',
        })
      } finally {
        this.$emit('loading', false)
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import "vars";

.switch-container {
  .switch {
    direction: rtl;
  }
}
</style>

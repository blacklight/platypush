<template>
  <div class="switch">
    <div class="col-10 label">
      <div class="name" v-text="value.name" />
    </div>

    <div class="col-2 switch pull-right">
      <ToggleSwitch :value="value.state" @input="toggle" />
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
  },

  data() {
    return {
      component: null,
    }
  },

  methods: {
    async toggle() {
      const response = await this.request('entities.execute', {
        id: this.value.id,
        action: 'toggle',
      })

      this.$emit('input', {
        ...this.value,
        state: response.on,
      })
    },
  },
}
</script>

<style lang="scss">
@import "vars";
</style>

<template>
  <form @submit.prevent="submit" class="name-editor">
    <input type="text" v-model="text" :disabled="disabled">
    <button type="submit">
      <i class="fas fa-circle-check" />
    </button>
    <button class="cancel" @click="$emit('cancel')" @touch="$emit('cancel')">
      <i class="fas fa-ban" />
    </button>
    <slot />
  </form>
</template>

<script>
export default {
  emits: ['input', 'cancel'],
  props: {
    value: {
      type: String,
    },

    disabled: {
      type: Boolean,
      deafult: false,
    },
  },

  data() {
    return {
      text: null,
    }
  },

  methods: {
    proxy(e) {
      this.$emit(e.type, e)
    },

    submit() {
      this.$emit('input', this.text)
      return false
    },
  },

  mounted() {
    this.text = this.value
  },
}
</script>

<style lang="scss" scoped>
.name-editor {
  background: #00000000;
  display: inline-flex;
  flex-direction: row;
  padding: 0;
  border: 0;
  border-radius: 0;
  box-shadow: none;

  button {
    border: none;
    background: none;
    padding: 0 0.5em;

    &.confirm {
      color: $selected-fg;
    }

    &.cancel {
      color: $error-fg;
    }
  }
}
</style>

<template>
  <button class="edit-btn"
          :title="title"
          @click="proxy($event)"
          @touch="proxy($event)"
          @input="proxy($event)">
    <i class="fas fa-pen-to-square" />
  </button>
</template>

<script>
export default {
  emits: ['input', 'click', 'touch'],
  props: {
    title: {
      type: String,
      default: 'Edit',
    },
  },

  methods: {
    proxy(e) {
      this.$emit(e.type, e)
    },
  },
}
</script>

<style lang="scss" scoped>
.edit-btn {
  border: 0;
  background: none;
  padding: 0 0.25em;
  margin-left: 0.25em;
  border: 1px solid rgba(0, 0, 0, 0);

  &:hover {
    color: $default-hover-fg;
    border: none;
  }
}
</style>

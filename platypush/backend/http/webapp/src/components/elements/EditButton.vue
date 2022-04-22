<template>
  <button class="edit-btn"
    @click="proxy($event)" @touch="proxy($event)" @input="proxy($event)"
  >
    <i class="fas fa-pen-to-square" />
  </button>
</template>

<script>
export default {
  emits: ['input', 'click', 'touch'],
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
    background: $hover-bg;
    border: 1px solid $selected-fg;
  }
}
</style>

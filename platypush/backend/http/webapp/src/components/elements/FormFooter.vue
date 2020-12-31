<template>
  <div class="form-footer">
    <slot />
  </div>
</template>

<script>
export default {
  name: "FormFooter"
}
</script>

<style lang="scss" scoped>
.form-footer {
  height: 5em;
  padding: 1em;
  text-align: right;
  border-top: $default-border-2;
}
</style>

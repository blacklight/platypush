<template>
  <div class="row plugin execute-container">
    <!-- Action executor container -->
    <main>
      <h1>Execute Action</h1>
      <ActionEditor />
    </main>
  </div>
</template>

<script>
import ActionEditor from '@/components/Action/ActionEditor'

export default {
  components: {
    ActionEditor,
  },
}
</script>

<style lang="scss" scoped>
@import "@/components/Action/common";

.execute-container {
  width: 100%;
  height: 100%;
  color: $default-fg-2;
  font-weight: 400;
  border-radius: 0 0 1em 1em;
  display: flex;
  flex-direction: column;
  align-items: center;

  main {
    width: 100%;
    max-width: 1000px;
    display: flex;
    flex-direction: column;
    box-shadow: $section-shadow;

    @include from($desktop) {
      margin: 1em;
      border-radius: 1em 1em 0 0;
    }

    :deep(.action-editor-container) {
      .action-editor {
        height: 100%;
      }
    }
  }
}
</style>

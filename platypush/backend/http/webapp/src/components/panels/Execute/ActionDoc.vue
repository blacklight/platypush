<template>
  <section class="doc-container" v-if="doc?.length">
    <h2>
      <div class="title">
        <i class="fas fa-book" /> &nbsp;
        <a :href="action?.doc_url">Action documentation</a>
      </div>
      <div class="buttons" v-if="action?.name">
        <button type="button" title="cURL command" v-if="curlSnippet?.length" @click="$emit('curl-modal')">
          <i class="fas fa-terminal" />
        </button>
      </div>
    </h2>

    <div class="doc html">
      <Loading v-if="loading" />
      <span v-html="doc" v-else />
    </div>
  </section>
</template>

<script>
import Loading from "@/components/Loading"

export default {
  name: 'ActionDoc',
  components: { Loading },
  emits: ['curl-modal'],
  props: {
    action: Object,
    doc: String,
    curlSnippet: String,
    loading: Boolean,
  }
}
</script>

<style lang="scss" scoped>
@import "common";
</style>

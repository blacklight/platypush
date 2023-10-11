<template>
  <section class="response">
    <h2 v-if="error != null || response != null">
      <span class="title">
        {{ error != null ? 'Error' : 'Output' }}
      </span>
      <span class="buttons">
        <button type="button" title="Copy to clipboard" @click="copyToClipboard(response)">
          <i class="fas fa-clipboard" />
        </button>
      </span>
    </h2>
    <div class="output response" v-if="response != null">
      <pre v-text="response" />
    </div>

    <div class="output error" v-else-if="error != null">
      <pre v-text="error" />
    </div>
  </section>
</template>

<script>
export default {
  name: 'Response',
  props: {
    response: String,
    error: String,
  },
}
</script>

<style lang="scss" scoped>
@import "common";
</style>

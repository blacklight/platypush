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
      <pre><code v-html="jsonResponse" v-if="jsonResponse != null" /><code v-text="response" v-else /></pre>
    </div>

    <div class="output error" v-else-if="error != null">
      <pre v-text="error" />
    </div>
  </section>
</template>

<script>
import 'highlight.js/lib/common'
import 'highlight.js/styles/stackoverflow-dark.css'
import hljs from "highlight.js"
import Utils from "@/Utils"

export default {
  name: 'Response',
  mixins: [Utils],
  props: {
    response: String,
    error: String,
  },

  computed: {
    isJSON() {
      try {
        return JSON.parse(this.response) != null
      } catch (e) {
        return false
      }
    },

    jsonResponse() {
      if (this.isJSON) {
        return hljs.highlight('json', this.response).value
      }

      return null
    }
  },
}
</script>

<style lang="scss" scoped>
@import "common";
</style>

<template>
  <div class="string renderer">
    <pre><code v-html="highlightedText" /></pre>
  </div>
</template>

<script>
import Mixin from './Mixin'

export default {
  mixins: [Mixin],
}
</script>

<style lang="scss" scoped>
@import "./style.scss";
</style>

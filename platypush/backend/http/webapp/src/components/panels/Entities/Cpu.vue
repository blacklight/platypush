<template>
  <div class="entity cpu-container">
    <div class="head">
      <div class="col-1 icon">
        <EntityIcon
          :entity="value"
          :loading="loading"
          :error="error" />
      </div>

      <div class="col-9 label">
        <div class="name" v-text="value.name" />
      </div>

      <div class="col-2 value" v-text="Math.round(value.percent * 100, 1) + '%'" />
    </div>
  </div>
</template>

<script>
import EntityMixin from "./EntityMixin"
import EntityIcon from "./EntityIcon"

export default {
  name: 'Cpu',
  components: {EntityIcon},
  mixins: [EntityMixin],
}
</script>

<style lang="scss" scoped>
@import "common";

.cpu-container {
  .head {
    .value {
      text-align: right;
      font-weight: bold;
    }
  }
}
</style>

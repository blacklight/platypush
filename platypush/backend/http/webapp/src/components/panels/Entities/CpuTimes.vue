<template>
  <div class="entity cpu-times-container">
    <div class="head">
      <div class="col-1 icon">
        <EntityIcon
          :entity="value"
          :loading="loading"
          :error="error" />
      </div>

      <div class="col-11 label">
        <div class="name" v-text="value.name" />
      </div>
    </div>
  </div>
</template>

<script>
import EntityMixin from "./EntityMixin"
import EntityIcon from "./EntityIcon"

export default {
  name: 'CpuTimes',
  components: {EntityIcon},
  mixins: [EntityMixin],
}
</script>

<style lang="scss" scoped>
@import "common";

.entity {
  .icon {
    margin-right: 1em;
  }
}
</style>

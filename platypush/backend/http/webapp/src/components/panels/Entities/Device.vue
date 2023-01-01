<template>
  <div class="entity device-container">
    <div class="head">
      <div class="col-1 icon">
        <EntityIcon
          :icon="value.meta?.icon || {}"
          :loading="loading"
          :error="error" />
      </div>

      <div class="col-12 label">
        <div class="name" v-text="value.name" />
      </div>
    </div>
  </div>
</template>

<script>
import EntityMixin from "./EntityMixin"
import EntityIcon from "./EntityIcon"

export default {
  name: 'Device',
  components: {EntityIcon},
  mixins: [EntityMixin],
}
</script>

<style lang="scss" scoped>
@import "common";

.device-container {
  .icon {
    margin-right: 1em;
  }
}
</style>

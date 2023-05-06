<template>
  <div class="entity device-container">
    <div class="head">
      <div class="icon">
        <EntityIcon
          :entity="value"
          :loading="loading"
          :error="error" />
      </div>

      <div class="label">
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
</style>

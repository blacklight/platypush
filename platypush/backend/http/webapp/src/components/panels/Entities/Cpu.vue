<template>
  <div class="entity cpu-container">
    <div class="head">
      <div class="col-1 icon">
        <EntityIcon :entity="value" :loading="loading" :error="error" />
      </div>

      <div class="label">
        <div class="name" v-text="value.name" />
      </div>

      <div class="value-container">
        <div class="value" v-text="Math.round(value.percent * 100, 1) + '%'" />
      </div>
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
</style>

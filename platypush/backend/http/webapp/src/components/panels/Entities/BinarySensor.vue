<template>
  <div class="entity sensor-container">
    <div class="head">
      <div class="icon">
        <EntityIcon :entity="value" :loading="loading" :error="error" />
      </div>

      <div class="label">
        <div class="name" v-text="value.name" />
      </div>

      <div class="value-container" v-if="value.value != null">
        <ToggleSwitch :value="value.value" :disabled="true" />
      </div>
    </div>
  </div>
</template>

<script>
import EntityMixin from "./EntityMixin"
import EntityIcon from "./EntityIcon"
import ToggleSwitch from "@/components/elements/ToggleSwitch"

export default {
  name: 'BinarySensor',
  components: {EntityIcon, ToggleSwitch},
  mixins: [EntityMixin],
}
</script>

<style lang="scss" scoped>
@import "common";
</style>

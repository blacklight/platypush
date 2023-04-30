<template>
  <div class="entity memory-stats-container" :class="{expanded: !isCollapsed}">
    <div class="head" @click.stop="isCollapsed = !isCollapsed">
      <div class="icon">
        <EntityIcon :entity="value" :loading="loading" :error="error" />
      </div>

      <div class="label">
        <div class="name" v-text="value.name" />
      </div>

      <div class="value-and-toggler">
        <div class="value" v-text="Math.round(value.percent * 100, 1) + '%'" />
        <div class="collapse-toggler" @click.stop="isCollapsed = !isCollapsed">
          <i class="fas"
            :class="{'fa-chevron-down': isCollapsed, 'fa-chevron-up': !isCollapsed}" />
        </div>
      </div>
    </div>

    <div class="body children attributes fade-in" v-if="!isCollapsed">
      <div class="child" v-if="value.total != null">
        <div class="label">
          <div class="name">Total</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertSize(value.total)" />
        </div>
      </div>

      <div class="child" v-if="value.available != null">
        <div class="label">
          <div class="name">Available</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertSize(value.available)" />
        </div>
      </div>

      <div class="child" v-if="value.used != null">
        <div class="label">
          <div class="name">Used</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertSize(value.used)" />
        </div>
      </div>

      <div class="child" v-if="value.free != null">
        <div class="label">
          <div class="name">Free</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertSize(value.free)" />
        </div>
      </div>

      <div class="child" v-if="value.active != null">
        <div class="label">
          <div class="name">Active</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertSize(value.active)" />
        </div>
      </div>

      <div class="child" v-if="value.inactive != null">
        <div class="label">
          <div class="name">Inactive</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertSize(value.inactive)" />
        </div>
      </div>

      <div class="child" v-if="value.buffers != null">
        <div class="label">
          <div class="name">Buffers</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertSize(value.buffers)" />
        </div>
      </div>

      <div class="child" v-if="value.cached != null">
        <div class="label">
          <div class="name">Cached</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertSize(value.cached)" />
        </div>
      </div>

      <div class="child" v-if="value.shared != null">
        <div class="label">
          <div class="name">Shared</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertSize(value.shared)" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import EntityMixin from "./EntityMixin"
import EntityIcon from "./EntityIcon"

export default {
  name: 'MemoryStats',
  components: {EntityIcon},
  mixins: [EntityMixin],

  data() {
    return {
      isCollapsed: true,
    }
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.entity {
  .head {
    .value {
      text-align: right;
      font-weight: bold;
    }
  }
}
</style>

<template>
  <div class="entity cpu-info-container">
    <div class="head" @click.stop="isCollapsed = !isCollapsed">
      <div class="col-1 icon">
        <EntityIcon
          :entity="value"
          :loading="loading"
          :error="error" />
      </div>

      <div class="col-10 label">
        <div class="name">CPU Info</div>
      </div>

      <div class="col-1 collapse-toggler" @click.stop="isCollapsed = !isCollapsed">
        <i class="fas"
          :class="{'fa-chevron-down': isCollapsed, 'fa-chevron-up': !isCollapsed}" />
      </div>
    </div>

    <div class="body children fade-in" v-if="!isCollapsed">
      <div class="child" v-if="value.architecture">
        <div class="col-s-12 col-m-6 label">
          <div class="name">Architecture</div>
        </div>
        <div class="value">
          <div class="name" v-text="value.architecture" />
        </div>
      </div>

      <div class="child" v-if="value.bits">
        <div class="label">
          <div class="name">Bits</div>
        </div>
        <div class="value">
          <div class="name" v-text="value.bits" />
        </div>
      </div>

      <div class="child" v-if="value.cores">
        <div class="label">
          <div class="name">Cores</div>
        </div>
        <div class="value">
          <div class="name" v-text="value.cores" />
        </div>
      </div>

      <div class="child" v-if="value.vendor">
        <div class="label">
          <div class="name">Vendor</div>
        </div>
        <div class="value">
          <div class="name" v-text="value.vendor" />
        </div>
      </div>

      <div class="child" v-if="value.brand">
        <div class="label">
          <div class="name">Brand</div>
        </div>
        <div class="value">
          <div class="name" v-text="value.brand" />
        </div>
      </div>

      <div class="child" v-if="value.frequency_advertised">
        <div class="label">
          <div class="name">Advertised Frequency</div>
        </div>
        <div class="value">
          <div class="name" v-text="displayedFrequency(value.frequency_advertised)" />
        </div>
      </div>

      <div class="child" v-if="value.frequency_actual">
        <div class="label">
          <div class="name">Actual Frequency</div>
        </div>
        <div class="value">
          <div class="name" v-text="displayedFrequency(value.frequency_actual)" />
        </div>
      </div>

      <div class="child" v-if="value.l1_instruction_cache_size">
        <div class="label">
          <div class="name">L1 Instruction Cache Size</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertSize(value.l1_instruction_cache_size)" />
        </div>
      </div>

      <div class="child" v-if="value.l1_data_cache_size">
        <div class="label">
          <div class="name">L1 Data Cache Size</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertSize(value.l1_data_cache_size)" />
        </div>
      </div>

      <div class="child" v-if="value.l2_cache_size">
        <div class="label">
          <div class="name">L2 Cache Size</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertSize(value.l2_cache_size)" />
        </div>
      </div>

      <div class="child" v-if="value.l3_cache_size">
        <div class="label">
          <div class="name">L3 Cache Size</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertSize(value.l3_cache_size)" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import EntityMixin from "./EntityMixin"
import EntityIcon from "./EntityIcon"

export default {
  name: 'CpuInfo',
  components: {EntityIcon},
  mixins: [EntityMixin],

  data() {
    return {
      isCollapsed: true,
    }
  },

  methods: {
    displayedFrequency(freq) {
      let unit = 'Hz'
      if (freq == null) {
        return null;
      }

      if (freq >= 1000000000) {
        freq /= 1000000000
        unit = 'GHz'
      }

      if (freq >= 1000000) {
        freq /= 1000000
        unit = 'MHz'
      }

      if (freq >= 1000) {
        freq /= 1000
        unit = 'kHz'
      }

      return `${freq.toFixed(2)} ${unit}`
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.entity {
  .head {
    padding: 0.25em;
  }
}

.collapse-toggler {
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 1;
  min-height: 3em;
  margin-left: 0;
  cursor: pointer;

  &:hover {
    color: $default-hover-fg;
  }
}

.child {
  margin: 0 -0.5em;
  padding: 0.5em 1em;

  &:not(:last-child) {
    border-bottom: 1px solid $border-color-1;
  }

  &:hover {
    cursor: initial;
  }

  .label {
    font-weight: bold;
    @include from($tablet) {
      @extend .col-m-6;
    }
  }

  .value {
    font-size: 0.95em;
    text-align: right;

    @include from($tablet) {
      @extend .col-m-6;
    }
  }
}
</style>

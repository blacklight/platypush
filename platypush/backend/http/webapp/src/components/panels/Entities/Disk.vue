<template>
  <div class="entity disk-container" :class="{expanded: !isCollapsed}">
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
      <div class="child" v-if="value.mountpoint?.length">
        <div class="label">
          <div class="name">Mountpoint</div>
        </div>
        <div class="value">
          <div class="name" v-text="value.mountpoint" />
        </div>
      </div>

      <div class="child" v-if="value.fstype?.length">
        <div class="label">
          <div class="name">Filesystem</div>
        </div>
        <div class="value">
          <div class="name" v-text="value.fstype" />
        </div>
      </div>

      <div class="child" v-if="value.opts?.length">
        <div class="label">
          <div class="name">Mount options</div>
        </div>
        <div class="value">
          <div class="name" v-text="value.opts" />
        </div>
      </div>

      <div class="child" v-if="value.total != null">
        <div class="label">
          <div class="name">Total space</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertSize(value.total)" />
        </div>
      </div>

      <div class="child" v-if="value.used != null">
        <div class="label">
          <div class="name">Used space</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertSize(value.used)" />
        </div>
      </div>

      <div class="child" v-if="value.free != null">
        <div class="label">
          <div class="name">Available space</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertSize(value.free)" />
        </div>
      </div>

      <div class="child" v-if="value.read_count != null">
        <div class="label">
          <div class="name">Number of reads</div>
        </div>
        <div class="value">
          <div class="name" v-text="value.read_count" />
        </div>
      </div>

      <div class="child" v-if="value.write_count != null">
        <div class="label">
          <div class="name">Number of writes</div>
        </div>
        <div class="value">
          <div class="name" v-text="value.write_count" />
        </div>
      </div>

      <div class="child" v-if="value.read_bytes != null">
        <div class="label">
          <div class="name">Bytes read</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertSize(value.read_bytes)" />
        </div>
      </div>

      <div class="child" v-if="value.write_bytes != null">
        <div class="label">
          <div class="name">Bytes written</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertSize(value.write_bytes)" />
        </div>
      </div>

      <div class="child" v-if="value.read_time != null">
        <div class="label">
          <div class="name">Read time</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertTime(value.read_time)" />
        </div>
      </div>

      <div class="child" v-if="value.write_time != null">
        <div class="label">
          <div class="name">Write time</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertTime(value.write_time)" />
        </div>
      </div>

      <div class="child" v-if="value.busy_time != null">
        <div class="label">
          <div class="name">Busy time</div>
        </div>
        <div class="value">
          <div class="name" v-text="convertTime(value.busy_time)" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import EntityMixin from "./EntityMixin"
import EntityIcon from "./EntityIcon"

export default {
  name: 'Disk',
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
</style>

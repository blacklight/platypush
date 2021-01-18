<template>
  <div class="browser-container">
    <Loading v-if="loading" />

    <div class="row item" @click="path = (path || '') + '/..'" v-if="path?.length && path !== '/'">
      <div class="col-10 left side">
        <i class="icon fa fa-folder" />
        <span class="name">..</span>
      </div>
    </div>

    <div class="row item" v-for="(file, i) in filteredFiles" :key="i" @click="path = file.path">
      <div class="col-10">
        <i class="icon fa" :class="{'fa-file': file.type !== 'directory', 'fa-folder': file.type === 'directory'}" />
        <span class="name">
          {{ file.name }}
        </span>
      </div>

      <div class="col-2 actions">
        <Dropdown>
          <DropdownItem icon-class="fa fa-play" text="Play"
                        @click="$emit('play', {type: 'file', url: `file://${file.path}`})"
                        v-if="isMedia && mediaExtensions.has(file.name.split('.').pop())" />
        </Dropdown>
      </div>
    </div>
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import Utils from "@/Utils";
import MediaUtils from "@/components/Media/Utils";
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";

export default {
  name: "Browser",
  components: {DropdownItem, Dropdown, Loading},
  mixins: [Utils, MediaUtils],
  emits: ['path-change'],

  props: {
    initialPath: {
      type: String,
    },

    isMedia: {
      type: Boolean,
    },

    filter: {
      type: String,
      default: '',
    },
  },

  data() {
    return {
      loading: false,
      path: this.initialPath,
      files: [],
    }
  },

  computed: {
    filteredFiles() {
      if (!this.filter?.length)
        return this.files

      return this.files.filter((file) => (file?.name || '').toLowerCase().indexOf(this.filter.toLowerCase()) >= 0)
    },
  },

  methods: {
    async refresh() {
      this.loading = true

      try {
        this.files = await this.request('file.list', {path: this.path})
        this.$emit('path-change', this.path)
      } finally {
        this.loading = false
      }
    },
  },

  mounted() {
    this.$watch(() => this.path, () => this.refresh())
    this.refresh()
  },
}
</script>

<style lang="scss" scoped>
@import "src/style/items";

.browser-container {
  .item {
    .actions {
      display: inline-flex;
      justify-content: right;
    }
  }
}
</style>

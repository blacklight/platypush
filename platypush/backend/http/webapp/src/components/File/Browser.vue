<template>
  <div class="browser">
    <Loading v-if="loading" />

    <div class="nav" ref="nav">
      <span class="path"
            v-for="(token, i) in pathTokens"
            :key="i"
            @click="path = pathTokens.slice(0, i + 1).join('/').slice(1)">
        <span class="token">
          {{ token }}
        </span>

        <span class="separator" v-if="(i > 0 || pathTokens.length > 1) && i < pathTokens.length - 1">
          <i class="fa fa-chevron-right" />
        </span>
      </span>
    </div>

    <div class="items" ref="items">
      <div class="row item"
           @click="onBack"
           v-if="(path?.length && path !== '/') || hasBack">
        <div class="col-10 left side">
          <i class="icon fa fa-folder" />
          <span class="name">..</span>
        </div>
      </div>

      <div class="row item" v-for="(file, i) in filteredFiles" :key="i" @click="onItemSelect(file)">
        <div class="col-10">
          <i class="icon fa" :class="{'fa-file': file.type !== 'directory', 'fa-folder': file.type === 'directory'}" />
          <span class="name">
            {{ file.name }}
          </span>
        </div>

        <div class="col-2 actions" v-if="fileActions.length">
          <Dropdown>
            <DropdownItem icon-class="fa fa-play" text="Play"
                          @click="$emit('play', {type: 'file', url: `file://${file.path}`})"
                          v-if="hasPlay && file.type !== 'directory'" />
          </Dropdown>
        </div>
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
  emits: ['back', 'path-change', 'play', 'input'],

  props: {
    hasBack: {
      type: Boolean,
      default: false,
    },

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

    hasPlay() {
      return this.isMedia && this.files.some((file) => this.mediaExtensions.has(file.name.split('.').pop()?.toLowerCase()))
    },

    fileActions() {
      if (!this.hasPlay)
        return []

      return [
        {
          iconClass: 'fa fa-play',
          text: 'Play',
          onClick: (file) => this.$emit('play', {type: 'file', url: `file://${file.path}`}),
        },
      ]
    },

    pathTokens() {
      if (!this.path?.length)
        return ['/']

      return ['/', ...this.path.split(/(?<!\\)\//).slice(1)]
    },
  },

  methods: {
    async refresh() {
      this.loading = true
      this.$nextTick(() => {
        // Scroll to the end of the path navigator
        this.$refs.nav.scrollLeft = 99999
        // Scroll to the top of the items list
        this.$refs.items.scrollTop = 0
      })

      try {
        this.files = await this.request('file.list', {path: this.path})
        this.$emit('path-change', this.path)
        this.setUrlArgs({path: decodeURIComponent(this.path)})
      } finally {
        this.loading = false
      }
    },

    onBack() {
      if (!this.path?.length || this.path === '/')
        this.$emit('back')
      else
        this.path = [...this.pathTokens].slice(0, -1).join('/').slice(1)
    },

    onItemSelect(file) {
      if (file.type === 'directory')
        this.path = file.path
      else
        this.$emit('input', file.path)
    },
  },

  watch: {
    initialPath() {
      this.path = this.initialPath
    },

    path() {
      this.refresh()
    },
  },

  mounted() {
    const args = this.getUrlArgs()
    if (args.path)
      this.path = args.path

    this.refresh()
  },

  unmounted() {
    this.setUrlArgs({path: null})
  },
}
</script>

<style lang="scss" scoped>
@import "src/style/items";

.browser {
  height: 100%;
  display: flex;
  flex-direction: column;

  .item {
    .actions {
      display: inline-flex;
      justify-content: right;
    }
  }

  .items {
    height: calc(100% - #{$nav-height});
    overflow: auto;
  }
}
</style>

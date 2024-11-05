<template>
  <div class="file-info">
    <Loading v-if="loading" />

    <div class="file-info-container" v-else-if="info">
      <div class="row item">
        <div class="label">Path</div>
        <div class="value">{{ info.path }}</div>
      </div>

      <div class="row item" v-if="info.size != null">
        <div class="label">Size</div>
        <div class="value">{{ convertSize(info.size) }}</div>
      </div>

      <div class="row item" v-if="info.created != null">
        <div class="label">Creation Date</div>
        <div class="value">{{ formatDate(info.created, true) }}</div>
      </div>

      <div class="row item" v-if="info.last_modified != null">
        <div class="label">Last Modified</div>
        <div class="value">{{ formatDate(info.last_modified, true) }}</div>
      </div>

      <div class="row item" v-if="info.mime_type != null">
        <div class="label">MIME type</div>
        <div class="value">{{ info.mime_type }}</div>
      </div>

      <div class="row item" v-if="info.permissions != null">
        <div class="label">Permissions</div>
        <div class="value">{{ info.permissions }}</div>
      </div>

      <div class="row item" v-if="info.owner != null">
        <div class="label">Owner ID</div>
        <div class="value">{{ info.owner }}</div>
      </div>

      <div class="row item" v-if="info.group != null">
        <div class="label">Group ID</div>
        <div class="value">{{ info.group }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import MediaUtils from "@/components/Media/Utils";
import Utils from "@/Utils";

export default {
  components: {Loading},
  mixins: [Utils, MediaUtils],

  props: {
    file: {
      type: String,
    },
  },

  data() {
    return {
      info: {},
      loading: false,
    }
  },

  methods: {
    async refresh() {
      this.loading = true

      try {
        this.info = (
          await this.request(
            'file.info', {files: [this.file]}
          )
        )[this.file]
      } finally {
        this.loading = false
      }
    },
  },

  watch: {
    file() {
      this.refresh()
    },
  },

  mounted() {
    this.refresh()
  },
}
</script>

<style lang="scss" scoped>
@import "src/style/items";

.file-info {
  width: 100%;
  height: 100%;

  .file-info-container {
    width: 100%;
    height: 100%;
  }

  .item {
    width: 100%;
    padding: 0.75em 0.5em;
  }

  .label {
    opacity: 0.7;
  }

  .value {
    text-align: right;
    flex-grow: 1;
    margin-left: 1.5em;
  }
}
</style>

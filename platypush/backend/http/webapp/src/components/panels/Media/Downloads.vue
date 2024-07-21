<template>
  <Loading v-if="loading" />

  <div class="media-downloads fade-in" v-else>
    <div class="no-content" v-if="!Object.keys(downloads).length">No media downloads in progress</div>

    <div class="no-content" v-else-if="!Object.keys(filteredDownloads).length">No media downloads match the filter</div>

    <div class="items" v-else>
      <div class="row item"
           :class="{selected: selectedItem === i}"
           :key="i"
           v-for="(media, i) in filteredDownloads"
           @click="selectedItem = i"
      >
        <div class="col-8 left side">
          <i class="icon fa" :class="{
            'fa-check': media.state.toLowerCase() === 'completed',
            'fa-play': media.state.toLowerCase() === 'downloading',
            'fa-pause': media.state.toLowerCase() === 'paused',
            'fa-times': media.state.toLowerCase() === 'cancelled',
            'fa-stop': media.state.toLowerCase() === 'idle',
            'fa-hourglass-half': media.state.toLowerCase() === 'started',
          }" />
          <div class="title" v-text="media.path || media.url" />
        </div>

        <div class="col-2 right side">
          <span v-text="displayProgress[i]" />
        </div>

        <div class="col-2 right side">
          <Dropdown title="Actions" icon-class="fa fa-ellipsis-h" @click="selectedItem = i">
            <DropdownItem icon-class="fa fa-play" text="Play"
                          @input="$emit('play', {url: `file:///${media.path}`})"
                          v-if="media.state.toLowerCase() === 'completed'" />
            <DropdownItem icon-class="fa fa-pause" text="Pause download" @input="pause(media)"
                          v-if="media.state.toLowerCase() === 'downloading' || media.state.toLowerCase() === 'started'" />
            <DropdownItem icon-class="fa fa-rotate-left" text="Resume download" @input="resume(media)"
                          v-if="media.state.toLowerCase() === 'paused'" />
            <DropdownItem icon-class="fa fa-eraser" text="Clear from queue" @input="clear(media)"
                          v-if="media.state.toLowerCase() === 'completed'" />
            <DropdownItem icon-class="fa fa-stop" text="Cancel" @input="cancel(media)"
                          v-if="media.state.toLowerCase() !== 'completed' && media.state.toLowerCase() !== 'cancelled'" />
            <DropdownItem icon-class="fa fa-trash" text="Remove file" @input="onDeleteSelected(media)"
                          v-if="media.state.toLowerCase() === 'completed' || media.state.toLowerCase() === 'cancelled'" />
            <DropdownItem icon-class="fa fa-info" text="Media info" @input="$refs.mediaInfo.isVisible = true" />
          </Dropdown>
        </div>
      </div>
    </div>

    <Modal ref="mediaInfo" title="Media info" width="80%">
      <div class="modal-body media-info" v-if="selectedItem != null && downloads[selectedItem]">
        <div class="row" v-if="downloads[selectedItem].name">
          <div class="attr">Path</div>
          <div class="value" v-text="downloads[selectedItem].path" />
        </div>

        <div class="row" v-if="downloads[selectedItem].url">
          <div class="attr">Remote URL</div>
          <div class="value">
            <a :href="downloads[selectedItem].url" target="_blank" v-text="downloads[selectedItem].url" />
          </div>
        </div>

        <div class="row" v-if="downloads[selectedItem].path">
          <div class="attr">Local URL</div>
          <div class="value">
            <a :href="localURL(downloads[selectedItem])"
               target="_blank" v-text="downloads[selectedItem].path" />
          </div>
        </div>

        <div class="row" v-if="downloads[selectedItem].state">
          <div class="attr">State</div>
          <div class="value" v-text="downloads[selectedItem].state" />
        </div>

        <div class="row" v-if="downloads[selectedItem].progress != null">
          <div class="attr">Progress</div>
          <div class="value" v-text="displayProgress[selectedItem]" />
        </div>

        <div class="row" v-if="downloads[selectedItem].size != null">
          <div class="attr">Size</div>
          <div class="value" v-text="convertSize(downloads[selectedItem].size)" />
        </div>

        <div class="row" v-if="downloads[selectedItem].started_at">
          <div class="attr">Started</div>
          <div class="value" v-text="formatDateTime(downloads[selectedItem].started_at)" />
        </div>

        <div class="row" v-if="downloads[selectedItem].ended_at">
          <div class="attr">Ended</div>
          <div class="value" v-text="formatDateTime(downloads[selectedItem].ended_at)" />
        </div>
      </div>
    </Modal>

    <ConfirmDialog
      ref="deleteConfirmDialog"
      title="Delete file"
      @input="rm"
      @close="mediaToDelete = null"
    >
      Are you sure you want to delete the downloaded file?
    </ConfirmDialog>
  </div>
</template>

<script>
import ConfirmDialog from "@/components/elements/ConfirmDialog";
import Loading from "@/components/Loading";
import Utils from "@/Utils";
import MediaUtils from "@/components/Media/Utils.vue"
import Modal from "@/components/Modal";
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";

export default {
  mixins: [Utils, MediaUtils],
  emits: [
    'play',
    'refresh',
  ],

  components: {
    ConfirmDialog,
    Dropdown,
    DropdownItem,
    Loading,
    Modal,
  },

  props: {
    downloads: {
      type: Object,
      default: () => ({}),
    },

    pluginName: {
      type: String,
      required: true,
    },

    filter: {
      type: String,
      default: '',
    },
  },

  data() {
    return {
      loading: false,
      selectedItem: null,
      mediaToDelete: null,
    }
  },

  computed: {
    relativeFiles() {
      if (this.selectedItem == null || !this.downloads[this.selectedItem]?.files?.length)
        return []

      return this.downloads[this.selectedItem].files.map((file) => file.split('/').pop())
    },

    displayProgress() {
      return Object.values(this.downloads).reduce((acc, value) => {
        let progress = this.round(value.progress, 2)
        let percent = progress != null ? `${progress}%` : 'N/A'
        if (value.state.toLowerCase() === 'completed')
          percent = '100%'

        acc[value.path] = percent
        return acc
      }, {})
    },

    filteredDownloads() {
      const filter = (this.filter || '').trim().toLowerCase()
      let downloads = Object.values(this.downloads)
      if (filter?.length) {
        downloads = downloads.filter((download) => {
          return download.path.toLowerCase().includes(filter) ||
            download.url.toLowerCase().includes(filter)
        })
      }

      return downloads.reduce((acc, download) => {
        acc[download.path] = download
        return acc
      }, {})
    },
  },

  methods: {
    async run(action, media) {
      this.loading = true
      try {
        await this.request(
          `${this.pluginName}.${action}`,
          {path: media.path}
        )
      } finally {
        this.loading = false
      }
    },

    async pause(media) {
      await this.run('pause_download', media)
    },

    async resume(media) {
      await this.run('resume_download', media)
    },

    async clear(media) {
      await this.run('clear_downloads', media)
      if (this.downloads[media.path])
        delete this.downloads[media.path]
    },

    async cancel(media) {
      await this.run('cancel_download', media)
    },

    async rm() {
      const media = this.mediaToDelete
      if (!media)
        return

      try {
        await this.request('file.unlink', {file: media.path})
      } finally {
        await this.clear(media)
      }
    },

    localURL(media) {
      return `${window.location.origin}/file?path=${encodeURIComponent(media.path)}`
    },

    onDeleteSelected(media) {
      this.mediaToDelete = media
      this.$refs.deleteConfirmDialog.show()
    },
  }
}
</script>

<style lang="scss" scoped>
@import "src/style/items";

.media-downloads {
  height: 100%;
  background: $background-color;

  .no-content {
    height: 100%;
  }

  .items {
    display: flex;
    flex-direction: column;
    height: 100%;
    flex: 1;
    overflow-y: auto;
  }
}

:deep(.modal-body) {
  .row {
    display: flex;
    border-bottom: $default-border;
    padding: .5em .25em;
    border-radius: .5em;

    &:hover {
      background-color: $hover-bg;
    }

    .attr {
      @extend .col-3;
      display: inline-flex;
    }

    .value {
      @extend .col-9;
      display: inline-flex;
      justify-content: right;

      &.nowrap {
        overflow: hidden;
        white-space: nowrap;
        text-overflow: clip;
      }
    }
  }
}

:deep(.modal-body) {
  .dropdown-container {
    .row {
      box-shadow: none;
      border: none;
    }

    button {
      border: none;
      background: none;

      &:hover {
        color: $default-hover-fg;
      }
    }
  }
}
</style>

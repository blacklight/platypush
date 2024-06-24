<template>
  <Loading v-if="loading" />

  <div class="torrent-transfers fade-in" v-else>
    <div class="no-content" v-if="!Object.keys(transfers).length">No torrent transfers in progress</div>

    <div class="row item" :class="{selected: selectedItem === i}" v-for="(torrent, i) in transfers" :key="i"
         @click="selectedItem = i">
      <div class="col-8 left side">
        <i class="icon fa" :class="{
          'fa-check': torrent.finish_date != null,
          'fa-play': !torrent.finish_date && torrent.state === 'downloading' && !torrent.paused,
          'fa-pause': !torrent.finish_date && torrent.state === 'downloading' && torrent.paused,
          'fa-stop': !torrent.finish_date && torrent.state === 'stopped',
        }" />
        <div class="title" v-text="torrent.name || torrent.hash || torrent.url" />
      </div>

      <div class="col-2 right side">
        <span v-text="`${torrent.progress}%`" />
      </div>

      <div class="col-2 right side">
        <Dropdown title="Actions" icon-class="fa fa-ellipsis-h" @click="selectedItem = i">
          <DropdownItem icon-class="fa fa-pause" text="Pause transfer" @click="$emit('pause', torrent)"
                        v-if="torrent.state === 'downloading' && !torrent.paused" />
          <DropdownItem icon-class="fa fa-play" text="Resume transfer" @click="$emit('resume', torrent)"
                        v-if="torrent.state === 'downloading' && torrent.paused" />
          <DropdownItem icon-class="fa fa-trash" text="Remove transfer" @click="$emit('remove', torrent)" />
          <DropdownItem icon-class="fa fa-folder" text="View files" @click="$refs.torrentFiles.isVisible = true" />
          <DropdownItem icon-class="fa fa-info" text="Torrent info" @click="$refs.torrentInfo.isVisible = true" />
        </Dropdown>
      </div>
    </div>

    <Modal ref="torrentInfo" title="Torrent info" width="80%">
      <div class="modal-body torrent-info" v-if="selectedItem != null && transfers[selectedItem]">
        <div class="row" v-if="transfers[selectedItem].name">
          <div class="attr">Name</div>
          <div class="value" v-text="transfers[selectedItem].name" />
        </div>

        <div class="row" v-if="transfers[selectedItem].state">
          <div class="attr">State</div>
          <div class="value" v-text="transfers[selectedItem].state" />
        </div>

        <div class="row">
          <div class="attr">Progress</div>
          <div class="value" v-text="`${transfers[selectedItem].progress || 0}%`" />
        </div>

        <div class="row">
          <div class="attr">DL rate</div>
          <div class="value" v-text="`${convertSize(transfers[selectedItem].download_rate || 0)}/s`" />
        </div>

        <div class="row">
          <div class="attr">UL rate</div>
          <div class="value" v-text="`${convertSize(transfers[selectedItem].upload_rate || 0)}/s`" />
        </div>

        <div class="row">
          <div class="attr">Size</div>
          <div class="value" v-text="convertSize(transfers[selectedItem].size || 0)" />
        </div>

        <div class="row" v-if="transfers[selectedItem].remaining_bytes">
          <div class="attr">Remaining</div>
          <div class="value" v-text="convertSize(transfers[selectedItem].remaining_bytes)" />
        </div>

        <div class="row">
          <div class="attr">URL</div>
          <div class="value nowrap">
            <a :href="transfers[selectedItem].url" target="_blank" v-text="transfers[selectedItem].url" />
          </div>
        </div>

        <div class="row">
          <div class="attr">Peers</div>
          <div class="value" v-text="transfers[selectedItem].peers || 0" />
        </div>

        <div class="row" v-if="transfers[selectedItem].start_date">
          <div class="attr">Started</div>
          <div class="value" v-text="formatDateTime(transfers[selectedItem].start_date)" />
        </div>

        <div class="row" v-if="transfers[selectedItem].finish_date">
          <div class="attr">Finished</div>
          <div class="value" v-text="formatDateTime(transfers[selectedItem].finish_date)" />
        </div>

        <div class="row" v-if="transfers[selectedItem].save_path">
          <div class="attr">Save path</div>
          <div class="value" v-text="transfers[selectedItem].save_path" />
        </div>

        <div class="row" v-if="transfers[selectedItem].files">
          <div class="attr">Files</div>
          <div class="value">
            <div class="file" v-for="(file, i) in transfers[selectedItem].files" :key="i">
              <a :href="`/file?path=${encodeURIComponent(file)}`" target="_blank" v-text="file" />
            </div>
          </div>
        </div>
      </div>
    </Modal>

    <Modal ref="torrentFiles" title="Torrent files" width="80%">
      <div class="modal-body torrent-files" v-if="selectedItem != null && transfers[selectedItem]">
        <div class="row" v-for="(file, i) in relativeFiles" :key="file">
          <div class="col-1 icon">
            <Dropdown v-if="isMedia && mediaExtensions.has(file.split('.').pop())">
              <DropdownItem icon-class="fa fa-play" text="Play"
                            @click="$emit('play', {url: `file://${transfers[selectedItem].files[i]}`, type: 'file'})" />
            </Dropdown>

            <i class="fa fa-file" v-else />
          </div>
          <div class="col-11 name" v-text="file" />
        </div>
      </div>
    </Modal>
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import Utils from "@/Utils";
import MediaUtils from "@/components/Media/Utils.vue"
import Modal from "@/components/Modal";
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";

export default {
  emits: [
    'pause',
    'play',
    'play-with-captions',
    'refresh',
    'remove',
    'resume',
  ],
  components: {Dropdown, DropdownItem, Loading, Modal},
  mixins: [Utils, MediaUtils],
  props: {
    isMedia: {
      type: Boolean,
      default: false,
    },

    transfers: {
      type: Object,
      default: () => ({}),
    },
  },

  data() {
    return {
      loading: false,
      selectedItem: null,
    }
  },

  computed: {
    relativeFiles() {
      if (this.selectedItem == null || !this.transfers[this.selectedItem]?.files?.length)
        return []

      return this.transfers[this.selectedItem].files.map((file) => file.split('/').pop())
    },
  },
}
</script>

<style lang="scss" scoped>
@import "src/style/items";

.torrent-transfers {
  height: 100%;
  background: $background-color;

  .no-content {
    height: 100%;
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

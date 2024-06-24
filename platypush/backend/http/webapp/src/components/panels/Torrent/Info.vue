<template>
  <div class="info">
    <div class="row">
      <div class="label">Title</div>
      <div class="value">{{ torrent.title }}</div>
    </div>

    <div class="row">
      <div class="label">URL</div>
      <div class="value">
        <button title="Open" @click="openInNewTab(torrent.url)">
          <i class="fas fa-up-right-from-square" />
        </button>

        <button title="Copy" @click="copyToClipboard(torrent.url)">
          <i class="fas fa-clipboard" />
        </button>
      </div>
    </div>

    <div class="row">
      <div class="label">Size</div>
      <div class="value">{{ convertSize(torrent.size) }}</div>
    </div>

    <div class="row">
      <div class="label">Seeders</div>
      <div class="value">{{ torrent.seeds }}</div>
    </div>

    <div class="row">
      <div class="label">Leechers</div>
      <div class="value">{{ torrent.peers }}</div>
    </div>

    <div class="row">
      <div class="label">Uploaded</div>
      <div class="value">{{ formatDate(torrent.created_at, true) }}</div>
    </div>

    <div class="row" v-if="torrent.description">
      <div class="label">Description</div>
      <div class="value">{{ torrent.description }}</div>
    </div>

    <div class="row" v-if="torrent.year">
      <div class="label">Year</div>
      <div class="value">{{ torrent.year }}</div>
    </div>
  </div>
</template>

<script>
import Utils from "@/Utils";

export default {
  mixins: [Utils],

  props: {
    torrent: {
      type: Object,
      default: () => ({}),
    },
  },

  methods: {
    openInNewTab(url) {
      window.open(url, "_blank");
    },
  },
}
</script>

<style lang="scss" scoped>
.info {
  min-width: 50vw;
  max-width: 800px;

  .row {
    display: flex;
    align-items: center;
    margin-bottom: 5px;
    border-bottom: $default-border;

    @include until($desktop) {
      flex-direction: column;
    }

    @include from($desktop) {
      flex-direction: row;
    }
  }

  .label {
    width: 10em;
    font-weight: bold;
    margin-right: 5px;
  }

  .value {
    width: calc(100% - 10em);
    flex: 1;
    text-align: right;

    button {
      background: none;
      border: none;
      cursor: pointer;

      i {
        font-size: 1.2em;
      }

      &:hover {
        color: $default-hover-fg;
      }
    }
  }
}
</style>

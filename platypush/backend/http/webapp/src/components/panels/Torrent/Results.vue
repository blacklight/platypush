<template>
  <div class="results-container">
    <div class="no-content" v-if="!results?.length">No results</div>
    <div class="results" ref="body" @scroll="onScroll" v-else>
      <div class="result" v-for="(result, i) in results" :key="i">
        <div class="info">
          <div class="title">{{ result.title }}</div>
          <div class="additional-info">
            <span class="info-pill size">
              <span class="label">
                <i class="fa fa-hdd" />
              </span>
              <span class="separator" />
              <span class="value">{{ convertSize(result.size) }}</span>
            </span>
            <span class="separator"> &vert; </span>

            <span class="info-pill seeds">
              <span class="label">
                <i class="fa fa-users" />
              </span>
              <span class="separator" />
              <span class="value">{{ result.seeds }}</span>
            </span>
            <span class="separator"> &vert; </span>

            <span class="info-pill created-at">
              <span class="label">
                <i class="fa fa-calendar" />
              </span>
              <span class="separator" />
              <span class="value">{{ formatDate(result.created_at, true) }}</span>
            </span>
            <span class="separator"> &vert; </span>
          </div>
        </div>

        <div class="actions">
          <button title="Torrent info" @click="$emit('info', i)">
            <i class="fa fa-info-circle" />
          </button>

          <button title="Download" @click="$emit('download', result.url)">
            <i class="fa fa-download" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Utils from "@/Utils";

export default {
  emits: ['download', 'info', 'next-page'],
  mixins: [Utils],

  props: {
    results: {
      type: Array,
      default: () => [],
    },

    page: {
      type: Number,
      default: 1,
    },
  },

  data() {
    return {
      scrollTimeout: null,
    }
  },

  methods: {
    onScroll() {
      const offset = this.$refs.body.scrollTop
      const bodyHeight = parseFloat(getComputedStyle(this.$refs.body).height)
      const scrollHeight = this.$refs.body.scrollHeight

      if (offset >= (scrollHeight - bodyHeight - 5)) {
        if (this.scrollTimeout || !this.results.length)
          return

        this.scrollTimeout = setTimeout(() => {
          this.scrollTimeout = null
        }, 250)

        this.$emit('next-page', this.page + 1)
      }
    },
  },

}
</script>

<style lang="scss" scoped>
.results-container {
  width: 100%;
  height: 100%;
  background: $background-color;
  display: flex;
  flex-wrap: wrap;

  .no-content {
    width: 100%;
    height: 100%;
    text-align: center;
  }

  .results {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
  }

  .result {
    width: 100%;
    display: flex;
    border-bottom: $default-border;
    gap: 1em;
    padding: .5em 0;
    cursor: pointer;

    &:hover {
      background: $hover-bg;
    }

    .info {
      width: calc(100% - 5em);
      padding: .5em;
    }

    .additional-info {
      font-size: .8em;
      opacity: .7;
      display: flex;

      .separator {
        font-size: 1.5em;
        margin-right: .5em;
      }

      .info-pill {
        display: flex;
        align-items: center;
        margin-right: .5em;

        .label {
          font-weight: bold;
        }

        .separator {
          margin: -.2em .25em 0 .25em;
          font-size: 2em;
        }
      }
    }

    .actions {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 5em;

      button {
        background: none;
        opacity: .8;
        border: none;
        padding: .25em;
        cursor: pointer;

        &:hover {
          color: $hover-fg;
        }

        &:first-child {
          margin-right: 1em;
        }
      }
    }
  }
}
</style>

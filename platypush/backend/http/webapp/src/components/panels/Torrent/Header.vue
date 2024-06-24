<template>
  <div class="header" :class="{'with-nav': withNav}">
    <div class="row">
      <div class="left side" :class="leftSideClasses">
        <form @submit.prevent="submit">
          <label class="search-box">
            <input
              type="search"
              :disabled="loading"
              :placeholder="placeholder"
              v-model="torrentURL"
              v-if="selectedView === 'transfers'"
            >

            <input
              type="search"
              :placeholder="placeholder"
              :value="query"
              ref="search"
              v-else-if="selectedView === 'search'"
            >
          </label>

          <span class="button-container">
            <button type="submit" title="Loading" disabled v-if="loading">
              <Loading />
            </button>

            <button type="submit" title="Add torrent URL" v-else-if="selectedView === 'transfers'">
              <i class="fa fa-download" />
            </button>

            <button type="submit" title="Search" v-else-if="selectedView === 'search'">
              <i class="fa fa-search" />
            </button>
          </span>
        </form>
      </div>

      <div class="right side col-1" v-if="!withNav">
        <button @click="$emit('toggle')" title="Toggle navigation">
          <i class="fa fa-bars" />
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import Loading from "@/components/Loading";

export default {
  name: "Header",
  emits: ['torrent-add', 'search', 'toggle'],
  components: {Loading},

  props: {
    query: {
      type: String,
      default: '',
    },

    loading: {
      type: Boolean,
      default: false,
    },

    withNav: {
      type: Boolean,
      default: false,
    },

    selectedView: {
      type: String,
      default: 'transfers',
    },
  },

  data() {
    return {
      torrentURL: '',
    }
  },

  computed: {
    placeholder() {
      if (this.selectedView === 'transfers') {
        return 'Add torrent URL'
      }

      return 'Search torrents'
    },

    leftSideClasses() {
      if (!this.withNav) {
        return {
          'col-12': true,
        }
      }

      return {
        'col-11': true,
      }
    },
  },

  methods: {
    submit() {
      const query = this.$refs?.search?.value?.trim()
      if (this.selectedView === 'transfers' && this.torrentURL?.length) {
        this.$emit('torrent-add', this.torrentURL)
      } else if (this.selectedView === 'search' && query?.length) {
        this.$emit('search', query)
      }
    }
  },
}
</script>

<style lang="scss" scoped>
@import "vars";

.header {
  width: 100%;
  height: $torrent-header-height;
  position: relative;
  background: $menu-panel-bg;
  padding: .5em;
  box-shadow: $border-shadow-bottom;

  .row {
    display: flex;
    align-items: center;
  }

  .side {
    display: inline-flex;
    align-items: center;

    &.right {
      position: absolute;
      font-size: 1.1em;
      right: calc(#{$torrent-nav-width} / 4);
      justify-content: right;
    }
  }

  :deep(button) {
    background: none;
    padding: 0 .25em;
    border: 0;

    &:hover {
      color: $default-hover-fg-2;
    }
  }

  form {
    width: 100%;
    display: flex;
    padding: 0;
    border: 0;
    border-radius: 0;
    box-shadow: none;
    background: initial;
  }

  .button-container {
    width: 3em;
    position: relative;
    padding: 0;
  }

  :deep(.loading) {
    width: 5em;
    font-size: 1em;
    left: -0.5em;
    border-radius: 0 1em 1em 0;
  }

  [type=submit] {
    width: 100%;
    height: 100%;
    background: $default-bg-4;
    border: $default-border-2;
    border-radius: 0 1em 1em 0;
    margin-left: -.5em;
    cursor: pointer;

    &:hover {
      background: $hover-bg-3;
    }
  }

  .search-box {
    width: 100%;
    max-width: 600px;
    margin-left: .5em;

    input[type=search] {
      width: 100%;
    }
  }
}
</style>

<template>
  <div class="header" :class="{'with-filter': filterVisible}">
    <div class="row">
      <div class="col-s-12 col-m-9 col-l-7 left side">
        <form @submit.prevent="$emit('torrent-add', torrentURL)">
          <label class="search-box">
            <input type="search" placeholder="Add torrent URL" v-model="torrentURL">
          </label>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Header",
  emits: ['torrent-add'],

  data() {
    return {
      torrentURL: '',
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
      justify-content: right;
    }
  }

  :deep(button) {
    background: none;
    padding: 0 .25em;
    border: 0;
    margin-right: .25em;

    &:hover {
      color: $default-hover-fg-2;
    }
  }

  form {
    width: 100%;
    padding: 0;
    border: 0;
    border-radius: 0;
    box-shadow: none;
    background: initial;
  }

  .search-box {
    width: 100%;
    margin-left: .5em;

    input[type=search] {
      width: 100%;
    }
  }
}
</style>

<template>
  <div class="header">
    <div class="row">
      <div class="col-s-8 col-m-7 left side">
        <label class="search-box">
          <input type="search"
                 placeholder="Filter"
                 v-model="filter"
                 @change="$emit('filter', $event.target.value)"
                 @keyup="$emit('filter', $event.target.value)">
        </label>
      </div>
    </div>
  </div>
</template>

<script>
import Utils from '@/Utils'

export default {
  mixins: [Utils],
  emits: [
    'filter',
  ],

  data() {
    return {
      filter: '',
    }
  },
}
</script>

<style lang="scss" scoped>
@import "./vars";

.header {
  width: 100%;
  height: $header-height;
  position: relative;
  background: $menu-panel-bg;
  padding: .5em;
  box-shadow: $border-shadow-bottom;

  :deep(button) {
    background: none;
    padding: 0 .5em;
    border: 0;

    &:hover {
      color: $default-hover-fg-2;
    }
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

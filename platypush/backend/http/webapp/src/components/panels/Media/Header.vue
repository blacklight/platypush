<template>
  <div class="header" :class="{'with-filter': filterVisible}">
    <div class="row">
      <div class="col-7 left side">
        <button title="Filter" @click="filterVisible = !filterVisible">
          <i class="fa fa-filter" />
        </button>

        <form @submit.prevent="search">
          <label class="search-box">
            <input type="search" placeholder="Search" v-model="query">
          </label>
        </form>
      </div>

      <div class="col-5 right side">
        <Players :plugin-name="pluginName" @select="$emit('select-player', $event)"
                 @status="$emit('player-status', $event)" />
        <Dropdown title="Actions" icon-class="fa fa-ellipsis-h">
          <DropdownItem text="Play URL" icon-class="fa fa-play-circle" />
        </Dropdown>
      </div>
    </div>

    <div class="row filter fade-in" :class="{hidden: !filterVisible}">
      <label v-for="source in Object.keys(sources)" :key="source">
        <input type="checkbox" v-model="sources[source]" />
        {{ source }}
      </label>
    </div>
  </div>
</template>

<script>
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";
import Players from "@/components/panels/Media/Players";
export default {
  name: "Header",
  components: {Players, DropdownItem, Dropdown},
  emits: ['search', 'select-player', 'player-status'],

  props: {
    pluginName: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      filterVisible: false,
      query: '',
      sources: {
        'file': true,
        'youtube': true,
        'torrent': true,
      },
    }
  },

  methods: {
    search() {
      const types = Object.keys(this.sources).filter((source) => this.sources[source])
      if (!this.query?.length || !types?.length)
        return

      this.$emit('search', {
        query: this.query,
        types: types,
      })
    },
  }
}
</script>

<style lang="scss" scoped>
$media-header-height: 3.3em;
$filter-header-height: 3em;

.header {
  width: 100%;
  height: $media-header-height;
  position: relative;
  background: $menu-panel-bg;
  padding: .5em;
  box-shadow: $border-shadow-bottom;

  .row {
    display: flex;
    align-items: center;
  }

  &.with-filter {
    height: calc(#{$media-header-height} + #{$filter-header-height});
  }

  .side {
    display: inline-flex;
    align-items: center;

    &.right {
      justify-content: right;
    }
  }

  ::v-deep(button) {
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

  .filter {
    position: absolute;
    top: $media-header-height;
    height: $filter-header-height;
    padding-bottom: 1em;

    label {
      display: inline-flex;
      flex-direction: row;
      margin-right: 1em;

      input {
        margin-right: .5em;
      }
    }
  }
}
</style>

<template>
  <div class="subtitles-container">
    <div class="items">
      <Loading v-if="loading" />
      <div class="row item" :class="{selected: selectedItem == null}" @click="selectedItem = null">
        <div class="col-1 icon">
          <i class="fa fa-ban" />
        </div>

        <div class="col-11 title">None</div>
      </div>

      <div class="row item" :class="{selected: selectedItem === i}" v-for="(sub, i) in items" :key="i"
           @click="selectedItem = i">
        <div class="col-1 icon">
          <i class="fa fa-file" v-if="sub.IsLocal" />
          <i class="flag-icon" :class="`flag-icon-${sub.ISO639}`" v-else-if="sub.ISO639" />
          <i class="fa fa-closed-captioning" v-else />
        </div>
        {{ sub.SubFileName }}
      </div>
    </div>

    <div class="footer">
      <button @click="$emit('select-subs', selectedItem == null ? null : items[selectedItem])">Select</button>
    </div>
  </div>
</template>

<script>
import Loading from "@/components/Loading"
import Utils from "@/Utils";

export default {
  name: "Subtitles",
  mixins: [Utils],
  components: {Loading},
  emits: ['select-subs'],
  props: {
    item: {
      type: Object,
      default: () => {},
    },
  },

  data() {
    return {
      loading: false,
      items: [],
      selectedItem: null,
    }
  },

  methods: {
    async refresh() {
      this.loading = true

      try {
        this.items = await this.request('media.subtitles.search', {resource: this.item.url, language: 'all'})
      } finally {
        this.loading = false
      }
    }
  },

  mounted() {
    this.refresh()
  },
}
</script>

<style lang="scss" scoped>
@import "src/style/items";
@import "~@/style/flag-icons.css";

.subtitles-container {
  .items {
    overflow: auto;
  }

  .footer {
    display: flex;
    justify-content: right;
    padding: 1em;
    background: $default-bg-6;
    box-shadow: $border-shadow-top;
  }
}
</style>

<script>
import MediaProvider from "@/components/panels/Media/Providers/Mixin";

export default {
  mixins: [MediaProvider],

  emits: [
    'add-to-playlist',
    'back',
    'download',
    'play',
    'play-with-opts',
    'select',
  ],

  props: {
    collection: {
      type: Object,
    },

    path: {
      type: Array,
      default: () => [],
    },
  },

  data() {
    return {
      items: [],
      loading_: false,
      selectedResult: null,
      sort: {
        attr: 'title',
        desc: false,
      },
    };
  },

  computed: {
    isLoading() {
      return this.loading_ || this.loading
    },

    sortedItems() {
      if (!this.items) {
        return []
      }

      return [...this.items].sort((a, b) => {
        const attr = this.sort.attr
        const desc = this.sort.desc
        let aVal = a[attr]
        let bVal = b[attr]

        if (typeof aVal === 'number' || typeof bVal === 'number') {
          aVal = aVal || 0
          bVal = bVal || 0
          return desc ? bVal - aVal : aVal - bVal
        }

        aVal = (aVal || '').toString().toLowerCase()
        bVal = (bVal || '').toString().toLowerCase()
        return desc ? bVal.localeCompare(aVal) : aVal.localeCompare(bVal)
      }).map((item) => {
        return {
          item_type: item.type,
          ...item,
          type: 'jellyfin',
        }
      })
    },
  },

  methods: {
    async refresh() {
      const collection = this.collection?.name
      if (!collection?.length) {
        return
      }

      this.loading_ = true
      try {
        this.items = await this.request(
          'media.jellyfin.search',
          { collection, limit: 1000 },
        )

      } finally {
        this.loading_ = false
      }
    },
  },

  watch: {
    collection() {
      this.refresh()
    },
  },
}
</script>

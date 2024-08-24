<template>
  <div class="browser-home">
    <div class="items" ref="items">
      <div class="row item" @click="$emit('back')" v-if="hasBack">
        <div class="icon-container">
          <i class="icon fa fa-chevron-left" />
        </div>
        <span class="name">Back</span>
      </div>

      <div class="row item" v-for="(item, name) in filteredItems" :key="name" @click="$emit('input', item)">
        <div class="icon-container">
          <img class="icon" :src="item.icon.url" v-if="item.icon?.url?.length" />
          <i class="icon" :class="item.icon?.['class'] || 'fas fa-folder'" v-else />
        </div>

        <span class="name">
          {{ name }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import Utils from "@/Utils";

export default {
  mixins: [Utils],
  emits: ['back', 'input'],

  props: {
    hasBack: {
      type: Boolean,
      default: false,
    },

    filter: {
      type: String,
      default: '',
    },

    items: {
      type: Object,
      required: true,
    },

    includeHome: {
      type: Boolean,
      default: true,
    },

    includeRoot: {
      type: Boolean,
      default: true,
    },
  },

  data() {
    return {
      userHome: null,
    }
  },

  computed: {
    allItems() {
      return Object.entries(
        {
          ...(this.includeRoot ? {
            Root: {
              name: 'Root',
              path: '/',
              icon: {
                'class': 'fas fa-hard-drive',
              }
            }
          } : {}),
          ...(this.includeHome && this.userHome ? {
            Home: {
              name: 'Home',
              path: this.userHome,
              icon: {
                'class': 'fas fa-home',
              }
            }
          } : {}),
          ...this.items,
        }
      ).reduce((acc, [name, item]) => {
        if (!item.type?.length) {
          item.type = 'directory'
        }

        acc[name] = {
          name,
          ...item,
        }
        return acc
      }, {})
    },

    filteredItems() {
      return Object.fromEntries(
          Object
            .entries(this.allItems)
            .filter(
              (entry) => entry[0].toLowerCase().includes(this.filter.toLowerCase())
            )
      )
    },
  },

  methods: {
    async getUserHome() {
      if (!this.userHome) {
        this.userHome = await this.request('file.get_user_home')
      }

      return this.userHome
    },
  },

  mounted() {
    this.getUserHome()
  },
}
</script>

<style lang="scss" scoped>
@import "src/style/items";

.browser-home {
  height: 100%;
  display: flex;
  flex-direction: column;

  .items {
    height: calc(100% - #{$nav-height});
    overflow: auto;
  }

  .icon-container {
    width: 2em;
    display: inline-flex;
    justify-content: center;

    img {
      max-width: calc(100% - 0.25em);
    }
  }
}
</style>

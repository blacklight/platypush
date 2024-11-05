<template>
  <div class="row plugin file-container">
    <Loading v-if="loading" />
    <div class="file-browser" v-else>
      <Header :filter="filter" @filter="filter = $event" />
      <Browser :initial-path="null" :filter="filter" :homepage="displayedBookmarks" />
    </div>
  </div>
</template>

<script>
import Browser from '@/components/File/Browser'
import Header from './Header'
import Loading from '@/components/Loading'
import Utils from '@/Utils'

export default {
  mixins: [Utils],
  components: {
    Browser,
    Header,
    Loading,
  },

  data() {
    return {
      bookmarks: {},
      configDir: null,
      filter: '',
      homeDir: null,
      loading: false,
    }
  },

  computed: {
    displayedBookmarks() {
      const items = {
        Root: {
          name: 'Root',
          path: '/',
          icon: {
            class: 'fas fa-hard-drive',
          },
        },
      }

      if (this.homeDir) {
        items.Home = {
          name: 'Home',
          path: this.homeDir,
          icon: {
            class: 'fas fa-home',
          },
        }
      }

      if (this.configDir) {
        items.Configuration = {
          name: 'Configuration',
          path: this.configDir,
          icon: {
            class: 'fas fa-cogs',
          },
        }
      }

      return {
        ...items,
        ...this.bookmarks,
      }
    },
  },

  methods: {
    async getConfig() {
      this.loading = true

      try {
        let configFile = null;
        [this.homeDir, this.bookmarks, configFile] = await Promise.all([
          this.request('file.get_user_home'),
          this.request('file.get_bookmarks'),
          this.request('config.get_config_file'),
        ])

        if (configFile) {
          this.configDir = configFile.split('/').slice(0, -1).join('/')
        }
      } finally {
        this.loading = false
      }
    },
  },

  mounted() {
    this.getConfig()
  },
}
</script>

<style lang="scss" scoped>
@import "./vars";

.file-container {
  display: flex;
  width: 100%;
  height: 100%;
  position: relative;

  .file-browser {
    width: 100%;
    height: calc(100% - #{$header-height});
    display: flex;
    flex-direction: column;
  }

  :deep(.browser) {
    width: 100%;
    height: 100%;
    background: $background-color;
  }
}
</style>

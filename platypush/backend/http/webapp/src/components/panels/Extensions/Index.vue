<template>
  <div class="row plugin extensions-container">
    <Loading v-if="loading" />

    <header>
      <div class="filter-container">
        <input type="text"
               ref="filter"
               placeholder="Extension name"
               v-model="filter"
               :disabled="loading" />
      </div>
    </header>

    <main>
      <div class="items">
        <div class="extension-container" v-for="name in extensionNames" :key="name">
          <div class="extension" v-if="matchesFilter(name)">
            <div class="item"
                 :class="{selected: name === selectedExtension}"
                 :data-name="name"
                 @click="onClick(name, false)">
              <ExtensionIcon :name="name" size="1.75em" />
              <span class="name">{{ extensions[name].name }}</span>
              <span class="enabled icon" title="Enabled" v-if="enabledExtensions[name]">
                <i class="enabled icon fas fa-circle-check" v-if="enabledExtensions[name]" />
              </span>
            </div>

            <div class="extension-body-container until tablet"
                 v-if="selectedExtension && name === selectedExtension">
              <Extension :extension="extensions[selectedExtension]"
                         :config="enabledExtensions[selectedExtension]"
                         :config-file="configFile" />
            </div>
          </div>
        </div>
      </div>

      <div class="extension-body-container from desktop"
           v-if="selectedExtension">
        <Extension :extension="extensions[selectedExtension]"
                   :config="enabledExtensions[selectedExtension]"
                   :config-file="configFile" />
      </div>
    </main>
  </div>
</template>

<script>
import Extension from "./Extension"
import ExtensionIcon from "@/components/elements/ExtensionIcon"
import Loading from "@/components/Loading"
import Utils from "@/Utils"
import { bus } from "@/bus"

export default {
  name: "Extensions",
  mixins: [Utils],
  components: {
    Extension,
    ExtensionIcon,
    Loading,
  },

  data() {
    return {
      loading: false,
      plugins: {},
      backends: {},
      enabledPlugins: {},
      enabledBackends: {},
      filter: '',
      selectedExtension: null,
      configFile: null,
      config: {},
    }
  },

  computed: {
    extensions() {
      const extensions = {}

      Object.entries(this.plugins).forEach(([name, plugin]) => {
        extensions[name] = {
          ...plugin,
          name: name,
        }
      })

      Object.entries(this.backends).forEach(([name, backend]) => {
        name = `backend.${name}`
        extensions[name] = {
          ...backend,
          name: name,
        }
      })

      return extensions
    },

    enabledExtensions() {
      return [this.enabledPlugins, this.enabledBackends].reduce((acc, extensions) => {
        Object.entries(extensions).forEach(([name, config]) => {
          acc[name] = config
        })

        return acc
      }, {})
    },

    extensionNames() {
      return Object.keys(this.extensions).sort()
    },
  },

  methods: {
    onClick(input, setFilter = true, setUrlArgs = true) {
      if (this.selectedExtension === input) {
        this.selectedExtension = null
      } else {
        this.onInput(input, setFilter, setUrlArgs)
      }
    },

    onInput(input, setFilter = true, setUrlArgs = true) {
      if (setFilter) {
        this.filter = input
      }

      const name = input?.toLowerCase()?.trim()
      if (name?.length && this.extensions[name]) {
        this.selectedExtension = name
        if (setUrlArgs)
          this.setUrlArgs({extension: name})

        const el = this.$el.querySelector(`.extensions-container .item[data-name="${name}"]`)
        if (el)
          el.scrollIntoView({behavior: 'smooth'})
      } else {
        this.selectedExtension = null
        if (setUrlArgs)
          this.setUrlArgs({})
      }
    },

    matchesFilter(extension) {
      if (!this.filter) {
        return true
      }

      return extension.includes(this.filter.toLowerCase())
    },

    async loadExtensions() {
      this.loading = true
      let [enabledPlugins, enabledBackends] = [[], []]

      try {
          [
            this.plugins,
            this.backends,
            enabledPlugins,
            enabledBackends,
            this.config,
          ] =
            await Promise.all([
              this.request('inspect.get_all_plugins'),
              this.request('inspect.get_all_backends'),
              this.request('inspect.get_enabled_plugins'),
              this.request('inspect.get_enabled_backends'),
              this.request('inspect.get_config'),
            ])
      } finally {
        this.loading = false
      }

      this.enabledPlugins = enabledPlugins.reduce((acc, name) => {
        acc[name] = this.config[name] || {}
        return acc
      }, {})

      this.enabledBackends = enabledBackends.reduce((acc, name) => {
        name = `backend.${name}`
        acc[name] = this.config[name] || {}
        return acc
      }, {})

      this.loadExtensionFromUrl()
      this.$watch('$route.hash', () => this.loadExtensionFromUrl())
    },

    async loadConfigFile() {
      this.configFile = await this.request('config.get_config_file')
    },

    loadExtensionFromUrl() {
      const extension = this.getUrlArgs().extension
      if (extension)
        this.$nextTick(() => this.onInput(extension, false, false))
    },
  },

  mounted() {
    this.loadConfigFile()
    this.loadExtensions()
    bus.on('update:extension', (ext) => this.onInput(ext, false))
    this.$nextTick(() => this.$refs.filter.focus())
  }
}
</script>

<style lang="scss" scoped>
@import "src/style/items";
@import "@/components/Action/common";

$header-height: 3.25em;

.extensions-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  margin-top: .15em;

  header {
    height: $header-height;
    padding: 0.5em;
    margin-bottom: 2px;
    box-shadow: $border-shadow-bottom;

    .filter-container {
      width: 100%;

      input {
        width: 100%;
      }
    }
  }

  main {
    height: calc(100% - #{$header-height} - 0.25em);
    min-height: calc(100% - #{$header-height} - 0.25em);
    background: $background-color;
    display: flex;
    flex-direction: row;
  }

  .items {
    height: 100%;
    flex-grow: 1;
    overflow: auto;
    border-bottom: $default-border-2;
  }

  .extension-container {
    .extension {
      display: flex;
      flex-direction: column;

      :deep(.item) {
        .extension-icon {
          margin-right: 0.5em;
        }
      }

      .item {
        width: 100%;
        display: flex;
        padding: 1em;
        position: relative;

        .icon {
          width: 2.5em;
          position: absolute;
          right: -1em;
          top: 0.65em;
        }

        &.selected {
          font-weight: bold;
        }
      }
    }
  }

  .extension-body-container.desktop {
    width: 70%;
    height: 100%;
    min-height: 100%;
    border-left: $default-border-2;
    border-bottom: $default-border-2;

    :deep(article) {
      height: 100%;
      overflow: auto;
    }
  }
}
</style>

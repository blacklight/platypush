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
            <div class="item name"
                 :class="{selected: name === selectedExtension}"
                 :data-name="name"
                 @click="onInput(name, false)"
                 v-text="extensions[name].name" />

            <div class="extension-body-container until tablet"
                 v-if="selectedExtension && name === selectedExtension">
              <Extension :extension="extensions[selectedExtension]" />
            </div>
          </div>
        </div>
      </div>

      <div class="extension-body-container from desktop"
           v-if="selectedExtension">
        <Extension :extension="extensions[selectedExtension]" />
      </div>
    </main>
  </div>
</template>

<script>
import Loading from "@/components/Loading"
import Utils from "@/Utils"
import Extension from "./Extension"
import { bus } from "@/bus"

export default {
  name: "Extensions",
  mixins: [Utils],
  components: {
    Extension,
    Loading,
  },

  data() {
    return {
      loading: false,
      plugins: {},
      backends: {},
      filter: '',
      selectedExtension: null,
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

    extensionNames() {
      return Object.keys(this.extensions).sort()
    },
  },

  methods: {
    onInput(input, setFilter = true) {
      if (setFilter) {
        this.filter = input
      }

      const name = input?.toLowerCase()?.trim()
      if (name?.length && name !== this.selectedExtension && this.extensions[name]) {
        this.selectedExtension = name
        const el = this.$el.querySelector(`.extensions-container .item[data-name="${name}"]`)
        if (el)
          el.scrollIntoView({behavior: 'smooth'})
      } else {
        this.selectedExtension = null
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

      try {
          [this.plugins, this.backends] =
            await Promise.all([
              this.request('inspect.get_all_plugins'),
              this.request('inspect.get_all_backends'),
            ])
      } finally {
        this.loading = false
      }
    },
  },

  mounted() {
    this.loadExtensions()
    bus.on('update:extension', (ext) => this.onInput(ext, false))
    this.$nextTick(() => this.$refs.filter.focus())
  }
}
</script>

<style lang="scss" scoped>
@import "src/style/items";
@import "../Execute/common";

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

      .name {
        padding: 1em;

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

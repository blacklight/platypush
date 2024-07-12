<template>
  <keep-alive>
    <div class="media-browser">
      <Loading v-if="loading" />

      <div class="media-index grid" v-else-if="!mediaProvider">
        <div class="item"
             v-for="(provider, name) in mediaProviders"
             :key="name"
             @click="mediaProvider = provider">
          <div class="icon">
            <i v-bind="providersMetadata[name].icon"
               :style="{ color: providersMetadata[name].icon?.color || 'inherit' }"
               v-if="providersMetadata[name].icon" />
          </div>
          <div class="name">
            {{ providersMetadata[name].name }}
          </div>
        </div>
      </div>

      <div class="media-browser-body" v-else-if="mediaProvider">
        <component
            :is="mediaProvider"
            :filter="filter"
            :selected-playlist="selectedPlaylist"
            @add-to-playlist="$emit('add-to-playlist', $event)"
            @back="back"
            @path-change="$emit('path-change', $event)"
            @play="$emit('play', $event)"
        />
      </div>
    </div>
  </keep-alive>
</template>

<script>
import { defineAsyncComponent, shallowRef } from "vue";
import Browser from "@/components/File/Browser";
import Loading from "@/components/Loading";
import Utils from "@/Utils";
import providersMetadata from "./Providers/meta.json";

export default {
  mixins: [Utils],
  emits: [
    'add-to-playlist',
    'back',
    'create-playlist',
    'path-change',
    'play',
    'remove-from-playlist',
    'remove-playlist',
    'rename-playlist',
  ],

  components: {
    Browser,
    Loading,
  },

  props: {
    filter: {
      type: String,
      default: '',
    },

    selectedPlaylist: {
      type: Object,
    },
  },

  data() {
    return {
      loading: false,
      mediaProvider: null,
      mediaProviders: {},
      providersMetadata: providersMetadata,
    }
  },

  computed: {
    mediaProvidersLookup() {
      return Object.keys(this.mediaProviders)
        .reduce((acc, key) => {
          acc[key.toLowerCase()] = key
          return acc
        }, {})
    },
  },

  methods: {
    back() {
      this.mediaProvider = null
      this.$emit('back')
    },

    registerMediaProvider(type) {
      const component = shallowRef(
        defineAsyncComponent(
          () => import(`@/components/panels/Media/Providers/${type}`)
        )
      )

      this.$options.components[type] = component
      this.mediaProviders[type] = component
    },

    async refreshMediaProviders() {
      const config = await this.request('config.get')
      this.mediaProviders = {}
      // The local File provider is always enabled
      this.registerMediaProvider('File')

      if (config.youtube)
        this.registerMediaProvider('YouTube')
    },

    async onPlaylistChange() {
      if (!this.selectedPlaylist)
        return

      const playlistType = this.selectedPlaylist.type?.toLowerCase()
      const playlistMediaProvider = this.mediaProvidersLookup[playlistType]

      if (playlistMediaProvider) {
        this.mediaProvider = this.mediaProviders[playlistMediaProvider]
      }
    },
  },

  watch: {
    selectedPlaylist() {
      this.onPlaylistChange()
    },
  },

  async mounted() {
    await this.refreshMediaProviders()
    await this.onPlaylistChange()
  },
}
</script>

<style lang="scss" scoped>
@import "./style.scss";

.media-browser {
  height: 100%;

  .media-browser-body {
    height: 100%;
  }
}
</style>

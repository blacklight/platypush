<template>
  <keep-alive>
    <div class="media-browser">
      <div class="media-index grid" v-if="!mediaProvider">
        <div class="item"
             v-for="(provider, name) in visibleMediaProviders"
             :key="name"
             @click="mediaProvider = provider">
          <div class="icon">
            <i v-bind="providersMetadata[name].icon"
               :style="{ color: providersMetadata[name].icon?.color || 'inherit' }"
               v-if="providersMetadata[name].icon?.class" />

            <img :src="providersMetadata[name].icon.url"
                 v-else-if="providersMetadata[name].icon?.url" />
          </div>
          <div class="name">
            {{ providersMetadata[name].name }}
          </div>
        </div>
      </div>

      <div class="media-browser-body" v-if="mediaProvider">
        <component
            :is="mediaProvider"
            :filter="filter"
            :loading="loading"
            :media-plugin="mediaPlugin"
            :selected-playlist="selectedPlaylist"
            :selected-channel="selectedChannel"
            @add-to-playlist="$emit('add-to-playlist', $event)"
            @back="back"
            @download="$emit('download', $event)"
            @download-audio="$emit('download-audio', $event)"
            @path-change="$emit('path-change', $event)"
            @play="$emit('play', $event)"
            @play-with-opts="$emit('play-with-opts', $event)"
            @view="$emit('view', $event)"
        />
      </div>
    </div>
  </keep-alive>
</template>

<script>
import { defineAsyncComponent, ref } from "vue";
import Browser from "@/components/File/Browser";
import Utils from "@/Utils";
import providersMetadata from "./Providers/meta.json";

export default {
  mixins: [Utils],
  emits: [
    'add-to-playlist',
    'back',
    'create-playlist',
    'download',
    'download-audio',
    'path-change',
    'play',
    'play-with-opts',
    'remove-from-playlist',
    'remove-playlist',
    'rename-playlist',
    'set-filter',
    'view',
  ],

  components: {
    Browser,
  },

  props: {
    filter: {
      type: String,
      default: '',
    },

    mediaPlugin: {
      type: String,
    },

    selectedPlaylist: {
      type: Object,
    },

    selectedChannel: {
      type: Object,
    },

    loading: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
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

    visibleMediaProviders() {
      return Object.entries(this.mediaProviders)
        .filter(([provider, component]) => component && (!this.filter || provider.toLowerCase().includes(this.filter.toLowerCase())))
        .reduce((acc, [provider, component]) => {
          acc[provider] = component
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
      const component = ref(
        defineAsyncComponent(
          () => import(`@/components/panels/Media/Providers/${type}`)
        )
      )

      this.$options.components[type] = component
      this.mediaProviders[type] = component
    },

    async refreshMediaProviders() {
      const config = this.$root.config
      this.mediaProviders = {}
      // The local File provider is always enabled
      this.registerMediaProvider('File')

      if (config.youtube)
        this.registerMediaProvider('YouTube')

      if (config['media.jellyfin'])
        this.registerMediaProvider('Jellyfin')
    },

    onPlaylistChange() {
      if (!this.selectedPlaylist)
        return

      const playlistType = this.selectedPlaylist.type?.toLowerCase()
      const playlistMediaProvider = this.mediaProvidersLookup[playlistType]

      if (playlistMediaProvider) {
        this.mediaProvider = this.mediaProviders[playlistMediaProvider]
      }
    },

    onChannelChange() {
      if (!this.selectedChannel)
        return

      const channelType = this.selectedChannel.type?.toLowerCase()
      const channelMediaProvider = this.mediaProvidersLookup[channelType]

      if (channelMediaProvider) {
        this.mediaProvider = this.mediaProviders[channelMediaProvider]
      }
    },

    updateView() {
      if (this.getUrlArgs().provider?.length) {
        const provider = this.getUrlArgs().provider
        const providerName = this.mediaProvidersLookup[provider.toLowerCase()]

        if (!providerName?.length)
          return

        this.mediaProvider = this.mediaProviders[providerName]
      }

      if (this.selectedPlaylist)
        this.onPlaylistChange()
      else if (this.selectedChannel)
        this.onChannelChange()
    },
  },

  watch: {
    $route() {
      this.$emit('set-filter', '')
    },

    mediaProvider(provider) {
      if (!provider) {
        this.setUrlArgs({provider: null})
        return
      }

      const providerName = Object.entries(this.mediaProviders)
        .filter((pair) => pair[1] === provider)?.[0]?.[0]?.toLowerCase()

      if (!providerName?.length)
        return

      this.setUrlArgs({provider: providerName})
    },

    selectedPlaylist() {
      this.onPlaylistChange()
    },

    selectedChannel() {
      this.onChannelChange()
    },
  },

  async mounted() {
    await this.refreshMediaProviders()
    this.updateView()
  },

  unmounted() {
    this.setUrlArgs({provider: null})
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

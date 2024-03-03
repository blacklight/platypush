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
            @back="mediaProvider = null"
            @path-change="$emit('path-change', $event)"
            @play="$emit('play', $event)" />
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
  emits: ['path-change', 'play'],
  mixins: [Utils],
  components: {
    Browser,
    Loading,
  },

  props: {
    filter: {
      type: String,
      default: '',
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

  methods: {
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
  },

  mounted() {
    this.refreshMediaProviders()
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

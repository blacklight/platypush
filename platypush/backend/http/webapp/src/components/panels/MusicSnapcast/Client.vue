<template>
  <div class="row client" :class="{offline: !connected}">
    <div class="col-s-12 col-m-3 name" v-text="config.name?.length ? config.name : host.name"
         @click="$emit('modal-show', {type: 'client', client: id, group: groupId, host: server.name})">
    </div>

    <div class="col-s-12 col-m-9 controls">
      <div class="col-10 slider-container">
        <Slider :range="[0, 100]" :value="config.volume.percent"
                @mouseup="$emit('volume-change', {host: server.name, client: id, volume: $event.target.value})" />
      </div>

      <div class="col-2 switch pull-right">
        <ToggleSwitch :value="!config.volume.muted"
                      @input="$emit('mute-toggle', {host: server.name, client: id, muted: !config.volume.muted})" />
      </div>
    </div>
  </div>
</template>

<script>
import ToggleSwitch from "@/components/elements/ToggleSwitch";
import Slider from "@/components/elements/Slider";

export default {
  name: "Client",
  components: {Slider, ToggleSwitch},
  emits: ['volume-change', 'mute-toggle', 'modal-show'],

  props: {
    config: {
      type: Object,
      required: true,
    },

    connected: {
      type: Boolean,
      default: false,
    },

    host: {
      type: Object,
      required: true,
    },

    id: {
      type: String,
      required: true,
    },

    groupId: {
      type: String,
      required: true,
    },

    lastSeen: {
      type: Object,
      default: () => {},
    },

    snapclient: {
      type: Object,
      required: true,
    },

    server: {
      type: Object,
      required: true,
    },
  },
}
</script>

<style lang="scss" scoped>
.client {
  @include until($tablet) {
    flex-direction: column;
    border-bottom: $default-border;
  }

  .name, .controls {
    @include until($tablet) {
      width: 100%;
      display: flex;
    }
  }

  &.offline {
    color: $disabled-fg;
  }

  &:hover {
    background: $hover-bg;
  }

  .name {
    @include until($tablet) {
      padding-bottom: .5em;
    }

    &:hover {
      color: $default-hover-fg;
      cursor: pointer;
    }
  }

  .slider-container {
    padding-right: 1em;
  }
}
</style>

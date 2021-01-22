<template>
  <div class="group">
    <div class="head">
      <div class="col-10 name" @click="$emit('modal-show', {type: 'group', group: id, host: server.name})">
        <i class="icon fa" :class="{'fa-play': stream.status === 'playing', 'fa-stop': stream.status !== 'playing'}"></i>
        {{ name || stream.id || id }}
      </div>

      <div class="col-2 switch pull-right">
        <ToggleSwitch :value="!muted"
                      @input="$emit('group-mute-toggle', {host: server.name, group: id, muted: !muted})" />
      </div>
    </div>

    <div class="body">
      <Client v-for="client in clients" :key="client.id"
              :config="client.config"
              :connected="client.connected"
              :server="server"
              :host="client.host"
              :groupId="id"
              :id="client.id"
              :lastSeen="client.lastSeen"
              :snapclient="client.snapclient"
              @modal-show="$emit('modal-show', $event)"
              @volume-change="$emit('client-volume-change', $event)"
              @mute-toggle="$emit('client-mute-toggle', $event)" />
    </div>
  </div>
</template>

<script>
import ToggleSwitch from "@/components/elements/ToggleSwitch";
import Client from "@/components/panels/MusicSnapcast/Client";

export default {
  name: "Group",
  components: {Client, ToggleSwitch},
  emits: ['group-mute-toggle', 'modal-show', 'client-volume-change', 'client-mute-toggle'],
  props: {
    id: {
      type: String,
    },

    clients: {
      type: Object,
      default: () => {},
    },

    muted: {
      type: Boolean,
    },

    name: {
      type: String,
    },

    stream: {
      type: Object,
    },

    server: {
      type: Object,
    },
  },
}
</script>

<style lang="scss" scoped>
.group {
  .head {
    display: flex;
    background: $default-bg-4;
    border-top: $default-border-2;
    border-bottom: $default-border-2;
    border-radius: 0;
    cursor: pointer;

    &:hover {
      color: $default-hover-fg;
    }
  }

  .head,
  .client {
    display: flex;
    align-items: center;
    padding: 1em .5em;
  }
}
</style>

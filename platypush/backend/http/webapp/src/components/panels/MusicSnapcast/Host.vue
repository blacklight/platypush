<template>
  <div class="host">
    <div class="header">
      <div class="col-10 name" @click="$emit('modal-show', {type: 'host', host: server.host.name})">
        <i class="icon fa fa-server"></i>
        {{ server.host.name }}
      </div>
      <div class="col-2 buttons pull-right">
        <button type="button" @click="collapsed = !collapsed">
          <i class="icon fa" :class="{'fa-chevron-up': !collapsed, 'fa-chevron-down': collapsed}"></i>
        </button>
      </div>
    </div>

    <div class="group-container" v-if="!collapsed">
      <Group v-for="(group, id) in groups" :key="id"
             :id="group.id"
             :name="group.name"
             :server="server.host"
             :muted="group.muted"
             :clients="group.clients"
             :stream="streams[group.stream_id]"
             @modal-show="$emit('modal-show', $event)"
             @group-mute-toggle="$emit('group-mute-toggle', $event)"
             @client-mute-toggle="$emit('client-mute-toggle', $event)"
             @client-volume-change="$emit('client-volume-change', $event)"
      />
    </div>
  </div>
</template>

<script>
import Group from "@/components/panels/MusicSnapcast/Group";

export default {
  name: "Host",
  emits: ['modal-show', 'group-mute-toggle', 'client-mute-toggle', 'client-volume-change'],
  components: {Group},

  props: {
    groups: {
      type: Object,
      default: () => {},
    },

    server: {
      type: Object,
      default: () => {},
    },

    streams: {
      type: Object,
      default: () => {},
    },
  },

  data() {
    return {
      collapsed: false,
    }
  },
}
</script>

<style lang="scss" scoped>
.host {
  width: 95%;
  max-width: 1000px;
  margin: 1em auto;
  border: $default-border-2;
  border-radius: .5em;
  box-shadow: $border-shadow-bottom-right;
  background: $default-bg-2;

  .header {
    padding: .5em;
    background: $default-bg-5;
    border-bottom: $default-border-2;
    border-radius: .5em .5em 0 0;
    display: flex;
    align-items: center;

    .name {
      text-transform: uppercase;

      &:hover {
        color: $default-hover-fg;
        cursor: pointer;
      }
    }

    .buttons {
      margin-bottom: 0;
    }

    button {
      padding: 0;
      border: 0;
      background: none;
      &:hover { color: $default-hover-fg; }
    }
  }
}
</style>

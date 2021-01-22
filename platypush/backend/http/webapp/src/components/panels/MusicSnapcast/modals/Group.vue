<template>
  <div class="info">
    <div class="section name">
      <div class="title">Name</div>
      <div class="row">
        <div class="name-value">
          <span class="name" v-text="group.name?.length ? group.name : 'default'" />
          <button class="pull-right" title="Rename" @click="renameGroup">
            <i class="fa fa-edit" />
          </button>
        </div>
      </div>
    </div>

    <div class="section clients" v-if="Object.keys(group?.clients || {}).length > 0">
      <div class="title">Clients</div>
      <div class="row" ref="groupClients" v-for="(client, id) in (clients || {})" :key="id">
        <label class="client" :for="'snapcast-client-' + client.id">
          <input type="checkbox"
                 class="client"
                 :id="`snapcast-client-${client.id}`"
                 :value="client.id"
                 :checked="client.id in group.clients"
                 :disabled="loading"
                 @input="$emit($event.target.checked ? 'add-client' : 'remove-client', client.id)">
          {{ client.host.name }}
        </label>
      </div>
    </div>

    <div class="section streams" v-if="group?.stream_id">
      <div class="title">Stream</div>
      <div class="row">
        <div class="label col-3">ID</div>
        <div class="value col-9">
          <label>
            <select ref="streamSelect" @change="$emit('stream-change', $event.target.value)">
              <option
                  v-for="(stream, id) in streams" :key="id"
                  v-text="streams[group.stream_id].id"
                  :name="stream.id"
                  :value="stream.id"
                  :disabled="loading"
                  :selected="stream.id === group.stream_id">
              </option>
            </select>
          </label>
        </div>
      </div>

      <div class="row" v-if="streams?.[group.stream_id]?.status">
        <div class="label col-m-3">Status</div>
        <div class="value col-m-9" v-text="streams[group.stream_id].status"></div>
      </div>

      <div class="row" v-if="streams?.[group?.stream_id]?.uri?.host">
        <div class="label col-s-12 col-m-3">Host</div>
        <div class="value col-s-12 col-m-9" v-text="streams[group.stream_id].uri.host"></div>
      </div>

      <div class="row" v-if="streams?.[group?.stream_id]?.uri?.path">
        <div class="label col-s-12 col-m-3">Path</div>
        <div class="value col-s-12 col-m-9" v-text="streams[group.stream_id].uri.path"></div>
      </div>

      <div class="row" v-if="streams?.[group?.stream_id]?.uri?.raw">
        <div class="label col-s-12 col-m-3">URI</div>
        <div class="value col-s-12 col-m-9" v-text="streams[group.stream_id].uri.raw"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "GroupModal",
  emits: ['add-client', 'remove-client', 'stream-change', 'rename-group'],
  props: {
    loading: {
      type: Boolean,
      default: false,
    },

    group: {
      type: Object,
    },

    clients: {
      type: Object,
    },

    streams: {
      type: Object,
    },
  },

  methods: {
    renameGroup() {
      const name = (prompt('New group name', this.group.name) || '').trim()
      if (!name?.length)
        return

      this.$emit('rename-group', name)
    }
  },
}
</script>

<style lang="scss" scoped>
.info {
  .row {
    display: flex;
    align-items: center;
  }

  .section {
    padding: 1.5em;

    .row {
      align-items: normal;
    }
  }

  label.client {
    width: 100%;
  }

  .title {
    font-size: 1em;
    padding-left: .5em;
    padding-bottom: .5em;
    margin-bottom: .5em;
    border-bottom: $default-border;
  }

  .client {
    display: flex;
    align-items: center;

    input {
      margin-right: .5em;
    }
  }

  .name-value {
    display: flex;
    align-items: center;

    button {
      background: none;
      border: none;
      margin: 0 1em;
      padding: 0;

      &:hover {
        color: $default-hover-fg-2;
      }
    }
  }
}
</style>

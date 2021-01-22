<template>
  <div class="client-modal">
    <div class="info" v-if="client">
      <div class="row">
        <div class="label col-s-12 col-m-3">ID</div>
        <div class="value col-s-12 col-m-9" v-text="client.id"></div>
      </div>

      <div class="row" v-if="client.config?.name?.length || client.host?.name">
        <div class="label col-s-12 col-m-3">Name</div>
        <div class="value col-s-12 col-m-9">
          <span class="name" v-text="client.config?.name || client.host?.name"></span>
          <button title="Rename" @click="renameClient">
            <i class="fa fa-edit" />
          </button>
        </div>
      </div>

      <div class="row">
        <div class="label col-s-12 col-m-3">Connected</div>
        <div class="value col-s-12 col-m-9" v-text="client.connected"></div>
      </div>

      <div class="row">
        <div class="label col-s-12 col-m-3">Volume</div>
        <div class="value col-s-12 col-m-9">{{ client.config.volume.percent }}%</div>
      </div>

      <div class="row">
        <div class="label col-s-12 col-m-3">Muted</div>
        <div class="value col-s-12 col-m-9" v-text="client.config.volume.muted"></div>
      </div>

      <div class="row">
        <div class="label col-s-12 col-m-3">Latency</div>
        <div class="value col-s-12 col-m-9" v-text="client.config.latency"></div>
      </div>

      <div class="row" v-if="client.host.ip && client.host.ip.length">
        <div class="label col-s-12 col-m-3">IP Address</div>
        <div class="value col-s-12 col-m-9" v-text="client.host.ip"></div>
      </div>

      <div class="row" v-if="client.host.mac && client.host.mac.length">
        <div class="label col-s-12 col-m-3">MAC Address</div>
        <div class="value col-s-12 col-m-9" v-text="client.host.mac"></div>
      </div>

      <div class="row" v-if="client.host.os && client.host.os.length">
        <div class="label col-s-12 col-m-3">OS</div>
        <div class="value col-s-12 col-m-9" v-text="client.host.os"></div>
      </div>

      <div class="row" v-if="client.host.arch && client.host.arch.length">
        <div class="label col-s-12 col-m-3">Architecture</div>
        <div class="value col-s-12 col-m-9" v-text="client.host.arch"></div>
      </div>

      <div class="row">
        <div class="label col-s-12 col-m-3">Client name</div>
        <div class="value col-s-12 col-m-9" v-text="client.snapclient.name"></div>
      </div>

      <div class="row">
        <div class="label col-s-12 col-m-3">Client version</div>
        <div class="value col-s-12 col-m-9" v-text="client.snapclient.version"></div>
      </div>

      <div class="row">
        <div class="label col-s-12 col-m-3">Protocol version</div>
        <div class="value col-s-12 col-m-9" v-text="client.snapclient.protocolVersion"></div>
      </div>
    </div>

    <div class="buttons">
      <div class="row">
        <button type="button" :disabled="loading" @click="removeClient">
          <i class="fas fa-trash" />
          <span class="name">Remove client</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ClientModal",
  emits: ['remove-client', 'rename-client'],
  props: {
    loading: {
      type: Boolean,
      default: false,
    },

    client: {
      type: Object,
    },
  },

  methods: {
    removeClient() {
      if (!window.confirm('Are you sure that you want to remove this client?'))
        return

      this.$emit('remove-client')
    },

    renameClient() {
      const name = (window.prompt('New client name',
          this.client.config.name?.length ? this.client.config.name : this.client.host.name) || '').trim()

      if (!name.length)
        return

      this.$emit('rename-client', name)
    },
  }
}
</script>

<style lang="scss" scoped>
.client-modal {
  max-height: 75vh;
  display: flex;
  flex-direction: column;

  .info {
    height: 80%;
    overflow: auto;
  }

  button {
    background: none;
    border: none;
    padding: 0;
    margin: 0 .5em;

    &:hover {
      color: $default-hover-fg-2;
    }
  }

  .buttons {
    height: 20%;
    margin: 0 !important;
    padding: 0 !important;

    .row {
      width: 100%;
      height: 100%;
      display: flex;
      justify-content: center;
      padding: 0;

      &:hover {
        background: none;
      }

      button {
        width: 100%;
        height: 100%;
        padding: 1em;
        color: #900;
        border-color: #900;

        .name {
          margin-left: .5em;
        }

        &:hover {
          background: $hover-bg;
        }
      }
    }
  }
}
</style>

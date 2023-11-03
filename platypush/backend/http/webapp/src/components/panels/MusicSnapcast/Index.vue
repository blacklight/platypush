<template>
  <div class="music-snapcast-container">
    <Loading v-if="loading" />

    <div class="info">
      <Modal title="Server info" ref="modalHost">
        <ModalHost :info="hosts[selectedHost]" v-if="selectedHost" />
      </Modal>
    </div>

    <div class="info">
      <Modal title="Group info" ref="modalGroup">
        <ModalGroup :group="hosts[selectedHost].groups[selectedGroup]" :streams="hosts[selectedHost].streams"
                    :clients="clientsByHost[selectedHost]" :loading="loading" @add-client="addClientToGroup"
                    @remove-client="removeClientFromGroup" @stream-change="streamChange"
                    @rename-group="renameGroup($event)" v-if="selectedGroup" />
      </Modal>
    </div>

    <div class="info">
      <Modal title="Client info" ref="modalClient">
        <ModalClient :client="hosts[selectedHost].groups[selectedGroup].clients[selectedClient]" :loading="loading"
                     @remove-client="removeClient" @rename-client="renameClient($event)" v-if="selectedClient" />
      </Modal>
    </div>

    <Host v-for="(host, id) in hosts" :key="id"
        :server="host.server"
        :streams="host.streams"
        :groups="host.groups"
        @group-mute-toggle="groupMute($event)"
        @client-mute-toggle="clientMute($event)"
        @client-volume-change="clientSetVolume($event)"
        @modal-show="onModalShow($event)" />
  </div>
</template>

<script>
import Modal from "@/components/Modal";
import Utils from "@/Utils";
import Host from "@/components/panels/MusicSnapcast/Host";
import ModalHost from "@/components/panels/MusicSnapcast/modals/Host";
import ModalGroup from "@/components/panels/MusicSnapcast/modals/Group";
import ModalClient from "@/components/panels/MusicSnapcast/modals/Client";
import Loading from "@/components/Loading";

export default {
  name: "MusicSnapcast",
  mixins: [Utils],
  components: {Loading, Modal, Host, ModalHost, ModalGroup, ModalClient},

  data: function() {
    return {
      loading: false,
      hosts: {},
      ports: {},
      selectedHost: null,
      selectedGroup: null,
      selectedClient: null,
    }
  },

  computed: {
    clientsByHost() {
      return Object.entries(this.hosts).reduce((hosts, [name, info]) => {
        hosts[name] = {}

        Object.values(info.groups).forEach((group) => {
          Object.entries(group.clients).forEach(([clientId, client]) => {
            hosts[name][clientId] = client
          })
        })

        return hosts
      }, {})
    },
  },

  methods: {
    parseServerStatus(status) {
      status.server.host.port = this.ports[status.server.host.name]
      this.hosts[status.server.host.name] = {
        ...status,
        groups: status.groups.map((group) => {
          return {
            ...group,
            clients: group.clients.reduce((clients, client) => {
              clients[client.id] = client
              return clients
            }, {}),
          }
        }).reduce((groups, group) => {
          groups[group.id] = group
          return groups
        }, {}),

        streams: status.streams.reduce((streams, stream) => {
          streams[stream.id] = stream
          return streams
        }, {}),
      }
    },

    async refresh() {
      this.loading = true

      try {
        const hosts = await this.request('music.snapcast.get_backend_hosts')
        const statuses = await Promise.all(Object.keys(hosts).map(
            async (host) => this.request('music.snapcast.status', {host: host, port: hosts[host]})
        ))

        this.hosts = {}
        statuses.forEach((status) => {
          this.ports[status.server.host.name] = hosts[status.server.host.name]
          this.parseServerStatus(status)
        })
      } finally {
        this.loading = false
      }
    },

    async refreshHost(host) {
      if (!(host in this.hosts))
        return

      this.parseServerStatus(await this.request('music.snapcast.status', {
        host: host,
        port: this.ports[host]
      }))
    },

    async addClientToGroup(clientId) {
      this.loading = true

      try {
        if (!this.selectedHost || !this.selectedGroup || !(clientId in this.clientsByHost[this.selectedHost]))
          return

        const clients = [...new Set([clientId,
          ...Object.keys(this.hosts[this.selectedHost].groups[this.selectedGroup].clients)])]

        await this.request('music.snapcast.group_set_clients', {
          host: this.selectedHost,
          port: this.ports[this.selectedHost],
          group: this.selectedGroup,
          clients: clients,
        })

        await this.refreshHost(this.selectedHost)
      } finally {
        this.loading = false
      }
    },

    async removeClientFromGroup(clientId) {
      this.loading = true

      try {
        if (!this.selectedHost || !this.selectedGroup || !(clientId in this.clientsByHost[this.selectedHost]))
          return

        const clients = new Set([...Object.keys(this.hosts[this.selectedHost].groups[this.selectedGroup].clients)])
        if (!clients.has(clientId))
          return

        clients.delete(clientId)

        await this.request('music.snapcast.group_set_clients', {
          host: this.selectedHost,
          port: this.ports[this.selectedHost],
          group: this.selectedGroup,
          clients: [...clients],
        })

        await this.refreshHost(this.selectedHost)
      } finally {
        this.loading = false
      }
    },

    async renameGroup(name) {
      this.loading = true

      try {
        if (!this.selectedHost || !this.selectedGroup)
          return

        await this.request('music.snapcast.set_group_name', {
          host: this.selectedHost,
          port: this.ports[this.selectedHost],
          group: this.selectedGroup,
          name: name,
        })

        await this.refreshHost(this.selectedHost)
      } finally {
        this.loading = false
      }
    },

    async renameClient(name) {
      this.loading = true

      try {
        if (!this.selectedHost || !this.selectedClient)
          return

        await this.request('music.snapcast.set_client_name', {
          host: this.selectedHost,
          port: this.ports[this.selectedHost],
          client: this.selectedClient,
          name: name,
        })

        await this.refreshHost(this.selectedHost)
      } finally {
        this.loading = false
      }
    },

    async removeClient() {
      this.loading = true

      try {
        if (!(this.selectedHost && this.selectedClient))
          return

        await this.request('music.snapcast.delete_client', {
          host: this.selectedHost,
          port: this.ports[this.selectedHost],
          client: this.selectedClient,
        })

        this.$refs.modalClient.close()
        await this.refreshHost(this.selectedHost)
      } finally {
        this.loading = false
      }
    },

    async streamChange(streamId) {
      this.loading = true

      try {
        await this.request('music.snapcast.group_set_stream', {
          host: this.selectedHost,
          port: this.ports[this.selectedHost],
          group: this.selectedGroup,
          stream_id: streamId,
        })

        await this.refreshHost(this.selectedHost)
      } finally {
        this.loading = false
      }
    },

    onClientUpdate(event) {
      Object.keys(this.hosts[event.host].groups).forEach((groupId) => {
        if (event.client.id in this.hosts[event.host].groups[groupId].clients) {
          this.hosts[event.host].groups[groupId].clients[event.client.id] = event.client
        }
      })
    },

    onGroupStreamChange(event) {
      this.hosts[event.host].groups[event.group].stream_id = event.stream
    },

    onServerUpdate(event) {
      this.parseServerStatus(event.server)
    },

    onStreamUpdate(event) {
      this.hosts[event.host].streams[event.stream.id] = event.stream
    },

    onClientVolumeChange(event) {
      Object.keys(this.hosts[event.host].groups).forEach((groupId) => {
        if (!(event.client in this.hosts[event.host].groups[groupId].clients))
          return

        if (event.volume != null)
          this.hosts[event.host].groups[groupId].clients[event.client].config.volume.percent = event.volume

        if (event.muted != null)
          this.hosts[event.host].groups[groupId].clients[event.client].config.volume.muted = event.muted
      })
    },

    onGroupMuteChange(event) {
      this.hosts[event.host].groups[event.group].muted = event.muted
    },

    modalShow(event) {
      switch(event.type) {
        case 'host':
          this.modal[event.type].info = this.hosts[event.host]
          break
        case 'group':
          this.modal[event.type].info.server = this.hosts[event.host].server
          this.modal[event.type].info.group = this.hosts[event.host].groups[event.group]
          this.modal[event.type].info.streams = this.hosts[event.host].streams
          this.modal[event.type].info.clients = {}

          for (const group of Object.values(this.hosts[event.host].groups)) {
            for (const client of Object.values(group.clients)) {
              this.modal[event.type].info.clients[client.id] = client
            }
          }

          break
        case 'client':
          this.modal[event.type].info = this.hosts[event.host].groups[event.group].clients[event.client]
          this.modal[event.type].info.server = this.hosts[event.host].server
          break
      }

      this.modal[event.type].visible = true
    },

    async groupMute(event) {
      await this.request('music.snapcast.mute', {
        group: event.group,
        host: event.host,
        port: this.ports[event.host],
        mute: event.muted,
      })

      await this.refreshHost(event.host)
    },

    async clientMute(event) {
      await this.request('music.snapcast.mute', {
        client: event.client,
        host: event.host,
        port: this.ports[event.host],
        mute: event.muted,
      })

      await this.refreshHost(event.host)
    },

    async clientSetVolume(event) {
      await this.request('music.snapcast.volume', {
        client: event.client,
        host: event.host,
        port: this.ports[event.host],
        volume: event.volume,
      })

      await this.refreshHost(event.host)
    },

    onModalShow(event) {
      switch (event.type) {
        case 'host':
          this.selectedHost = event.host
          this.$refs.modalHost.show()
          break

        case 'group':
          this.selectedHost = event.host
          this.selectedGroup = event.group
          this.$refs.modalGroup.show()
          break

        case 'client':
          this.selectedHost = event.host
          this.selectedGroup = event.group
          this.selectedClient = event.client
          this.$refs.modalClient.show()
          break
      }
    }
  },

  mounted() {
    this.refresh()

    this.subscribe(this.onClientUpdate, null,
        'platypush.message.event.music.snapcast.ClientConnectedEvent',
        'platypush.message.event.music.snapcast.ClientDisconnectedEvent',
        'platypush.message.event.music.snapcast.ClientNameChangeEvent')

    this.subscribe(this.onGroupStreamChange, null, 'platypush.message.event.music.snapcast.GroupStreamChangeEvent')
    this.subscribe(this.onServerUpdate, null, 'platypush.message.event.music.snapcast.ServerUpdateEvent')
    this.subscribe(this.onStreamUpdate, null, 'platypush.message.event.music.snapcast.StreamUpdateEvent')
    this.subscribe(this.onClientVolumeChange, null, 'platypush.message.event.music.snapcast.ClientVolumeChangeEvent')
    this.subscribe(this.onGroupMuteChange, null, 'platypush.message.event.music.snapcast.GroupMuteChangeEvent')
  },
}
</script>

<style lang="scss" scoped>
.music-snapcast-container {
  width: 100%;
  overflow: auto;
  background: $background-color;
}

:deep(.info) {
  .modal {
    .content {
      width: 90%;
      max-width: 800px;
    }

    .body {
      padding: 0;
    }
  }

  .row {
    display: flex;
    align-items: center;
    border-radius: .75em;
    padding: 1em;

    @include until($tablet) {
      flex-direction: column;
      border-bottom: $default-border;
    }

    @include from($desktop) {
      padding: 1em 2em;
    }

    .label {
      margin-bottom: 0;
    }

    .value {
      display: flex;

      @include from($tablet) {
        justify-content: right;
      }

      @include until($tablet) {
        width: 100%;
        margin-left: 0;
      }
    }

    @include until($tablet) {
      .label {
        width: 100%;
        display: flex;
      }
    }

    &:nth-child(odd) {
      background: $background-color;
    }

    &:nth-child(even) {
      background: $default-bg-3;
    }

    &:hover {
      background: $hover-bg;
    }
  }

  .buttons {
    background: initial;
    margin-top: 1.5em;
    padding-top: 1.5em;
    border-top: $default-border-2;
    display: flex;
    justify-content: center;
  }
}

@media screen and (max-width: calc(#{$tablet} - 1)) {
  .music-snapcast-container {
    .modal {
      width: 95vw;
    }
  }
}

@media screen and (min-width: $tablet) {
  .music-snapcast-container {
    .modal {
      width: 70vw;
    }
  }
}

@media screen and (min-width: $desktop) {
  .music-snapcast-container {
    .modal {
      width: 45vw;
    }
  }
}
</style>

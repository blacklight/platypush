<template>
  <div class="item node" :class="{selected: selected}">
    <div class="row name header vertical-center" :class="{selected: selected}"
         v-text="node.name && node.name.length ? node.name : `<Node ${node.node_id}>`" @click="$emit('select')" />

    <div class="params" v-if="selected">
      <div class="row">
        <div class="param-name">Name</div>
        <div class="param-value">
          <div class="edit-cell" :class="{hidden: !editMode.name}">
            <form ref="nameForm" @submit.prevent="editName">
              <label>
                <input type="text" name="name" :value="node.name" :disabled="commandRunning">
              </label>

              <span class="buttons">
                <button type="button" class="btn btn-default" @click="editMode.name = false">
                  <i class="fas fa-times" />
                </button>

                <button type="submit" class="btn btn-default" :disabled="commandRunning">
                  <i class="fa fa-check" />
                </button>
              </span>
            </form>
          </div>

          <div :class="{hidden: editMode.name}">
            <span v-text="node.name?.length ? node.name : `<Node ${node.node_id}>`" />
            <span class="buttons">
              <button type="button" class="btn btn-default" @click="onEditMode('name')" :disabled="commandRunning">
                <i class="fa fa-edit"></i>
              </button>
            </span>
          </div>
        </div>
      </div>

      <div class="row" v-if="node.location && node.location.length">
        <div class="param-name">Location</div>
        <div class="param-value" v-text="node.location" />
      </div>

      <div class="row">
        <div class="param-name">Type</div>
        <div class="param-value" v-text="node.type" />
      </div>

      <div class="row">
        <div class="param-name">Role</div>
        <div class="param-value" v-text="node.role" />
      </div>

      <div class="row">
        <div class="param-name">Node ID</div>
        <div class="param-value" v-text="node.node_id" />
      </div>

      <div class="row" v-if="node.neighbours.length">
        <div class="param-name">Neighbours</div>
        <div class="param-value">
          <div class="row pull-right" v-for="(neighbour, i) in node.neighbours" :key="i" v-text="neighbour" />
        </div>
      </div>

      <div class="row">
        <div class="param-name">Is Ready</div>
        <div class="param-value" v-text="node.is_ready" />
      </div>

      <div class="row">
        <div class="param-name">Is Failed</div>
        <div class="param-value" v-text="node.is_failed" />
      </div>

      <div class="row">
        <div class="param-name">Product ID</div>
        <div class="param-value" v-text="node.manufacturer_id" />
      </div>

      <div class="row">
        <div class="param-name">Product Type</div>
        <div class="param-value" v-text="node.product_type" />
      </div>

      <div class="row" v-if="node.product_name?.length">
        <div class="param-name">Product Name</div>
        <div class="param-value" v-text="node.product_name" />
      </div>

      <div class="row">
        <div class="param-name">Manufacturer ID</div>
        <div class="param-value" v-text="node.manufacturer_id" />
      </div>

      <div class="row" v-if="node.manufacturer_name?.length">
        <div class="param-name">Manufacturer Name</div>
        <div class="param-value" v-text="node.manufacturer_name" />
      </div>

      <div class="row">
        <div class="param-name">Capabilities</div>
        <div class="param-value" v-text="node.capabilities.join(', ')" />
      </div>

      <div class="row">
        <div class="param-name">Command Classes</div>
        <div class="param-value" v-text="node.command_classes.join(', ')" />
      </div>

      <div class="row">
        <div class="param-name">Groups</div>
        <div class="param-value" v-text="Object.values(node.groups).map((g) => g.label || '').join(', ')" />
      </div>

      <div class="row">
        <div class="param-name">Home ID</div>
        <div class="param-value" v-text="node.home_id.toString(16)" />
      </div>

      <div class="row">
        <div class="param-name">Is Awake</div>
        <div class="param-value" v-text="node.is_awake" />
      </div>

      <div class="row">
        <div class="param-name">Is Locked</div>
        <div class="param-value" v-text="node.is_locked" />
      </div>

      <div class="row" v-if="node.last_update">
        <div class="param-name">Last Update</div>
        <div class="param-value" v-text="node.last_update" />
      </div>

      <div class="row" v-if="node.last_update">
        <div class="param-name">Max Baud Rate</div>
        <div class="param-value" v-text="node.max_baud_rate" />
      </div>

      <div class="section actions">
        <div class="header">
          <div class="title">Actions</div>
        </div>

        <div class="body">
          <div class="row error" v-if="node.is_failed" @click="removeFailedNode">
            <div class="param-name">Remove Failed Node</div>
            <div class="param-value">
              <i class="fa fa-trash" />
            </div>
          </div>

          <div class="row error" v-if="node.is_failed" @click="replaceFailedNode">
            <div class="param-name">Replace Failed Node</div>
            <div class="param-value">
              <i class="fa fa-sync-alt" />
            </div>
          </div>

          <div class="row" @click="heal">
            <div class="param-name">Heal Node</div>
            <div class="param-value">
              <i class="fas fa-wrench" />
            </div>
          </div>

          <div class="row" @click="replicationSend">
            <div class="param-name">Replicate info to secondary controller</div>
            <div class="param-value">
              <i class="fa fa-clone" />
            </div>
          </div>

          <div class="row" @click="requestNetworkUpdate">
            <div class="param-name">Request network update</div>
            <div class="param-value">
              <i class="fas fa-wifi" />
            </div>
          </div>

          <div class="row" @click="requestNeighbourUpdate">
            <div class="param-name">Request neighbours update</div>
            <div class="param-value">
              <i class="fas fa-network-wired" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Utils from "@/Utils";

export default {
  name: "Node",
  emits: ['select'],
  mixins: [Utils],

  props: {
    node: {
      type: Object,
      required: true,
    },

    selected: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      commandRunning: false,
      editMode: {
        name: false,
      },
    }
  },

  methods: {
    async removeFailedNode() {
      if (this.commandRunning) {
        this.notify({
          text: 'A command is already running'
        })

        return
      }

      if (!confirm('Are you sure that you want to remove this node?'))
        return

      this.commandRunning = true
      try {
        await this.request('zwave.remove_node', {
          node_id: this.node.node_id,
        })
      } finally {
        this.commandRunning = false
      }
    },

    async replaceFailedNode() {
      if (this.commandRunning) {
        this.notify({
          text: 'A command is already running'
        })

        return
      }

      if (!confirm('Are you sure that you want to replace this node?'))
        return

      this.commandRunning = true
      try {
        await this.request('zwave.replace_node', {
          node_id: this.node.node_id,
        })
      } finally {
        this.commandRunning = false
      }
    },

    async replicationSend() {
      if (this.commandRunning) {
        this.notify({
          text: 'A command is already running'
        })

        return
      }

      this.commandRunning = true
      try {
        await this.request('zwave.replication_send', {
          node_id: this.node.node_id,
        })
      } finally {
        this.commandRunning = false
      }
    },

    async requestNetworkUpdate() {
      if (this.commandRunning) {
        this.notify({
          text: 'A command is already running'
        })

        return
      }

      this.commandRunning = true
      try {
        await this.request('zwave.request_network_update', {
          node_id: this.node.node_id,
        })
      } finally {
        this.commandRunning = false
      }
    },

    async requestNeighbourUpdate() {
      if (this.commandRunning) {
        this.notify({
          text: 'A command is already running'
        })

        return
      }

      this.commandRunning = true
      try {
        await this.request('zwave.request_node_neighbour_update', {
          node_id: this.node.node_id,
        })
      } finally {
        this.commandRunning = false
      }
    },

    onEditMode(mode) {
      this.editMode[mode] = true
      const form = this.$refs[mode + 'Form']
      const input = form.querySelector('input[type=text]')

      setTimeout(() => {
        input.focus()
        input.select()
      }, 10)
    },

    async editName(event) {
      const name = event.target.querySelector('input[name=name]').value
      this.commandRunning = true

      try {
        await this.request('zwave.set_node_name', {
          node_id: this.node.node_id,
          new_name: name,
        })
      } finally {
        this.commandRunning = false
      }

      this.editMode.name = false
    },

    async heal() {
      if (this.commandRunning) {
        console.log('A command is already running')
        return
      }

      this.commandRunning = true
      try {
        await this.request('zwave.node_heal', {
          node_id: this.node.node_id,
        })
      } finally {
        this.commandRunning = false
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common";
</style>

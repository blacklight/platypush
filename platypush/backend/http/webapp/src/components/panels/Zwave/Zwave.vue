<template>
  <div class="zwave-container">
    <Modal title="Network info" ref="networkInfoModal">
      <div class="network-info">
        <Loading v-if="loading.status" />

        <div class="params" v-else>
          <div class="row">
            <div class="param-name">State</div>
            <div class="param-value" v-text="status.state"></div>
          </div>

          <div class="row">
            <div class="param-name">Device</div>
            <div class="param-value" v-text="status.device"></div>
          </div>

          <div class="section">
            <div class="header">
              <div class="title">Statistics</div>
            </div>

            <div class="body">
              <div class="row"
                   v-for="(value, name) in status.stats"
                   :key="name">
                <div class="param-name" v-text="name"></div>
                <div class="param-value" v-text="value"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Modal>

    <Modal title="Add nodes to group" ref="addNodesToGroupModal">
      <div class="group-add">
        <div class="params">
          <div class="section">
            <div class="header">
              <div class="title">Select nodes to add</div>
            </div>

            <div class="body" v-if="selected.groupId != null">
              <div class="row clickable" @click="addToGroup(node.node_id, selected.groupId)" :key="node.node_id"
                   v-for="node in Object.values(nodes || {}).filter(
                       (n) => groups[selected.groupId].associations.indexOf(n.node_id) < 0)">
                <div class="param-name" v-text="node.name"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Modal>

    <Alert title="" ref="noNodeNameModal">
      No node name specified
    </Alert>

    <Modal title="Add new node" ref="addNodeModal">
      <div class="node-add">
        <div class="body">
          <form class="add-node-form" ref="addNodeForm" @submit.prevent="addNode()">
            <div class="fields">
              <input type="text" name="name" placeholder="Node name">
              <input type="text" name="location" placeholder="Node location (optional)">
              <input type="number" name="timeout" value="30" placeholder="Timeout (in seconds)">
            </div>

            <div class="buttons">
              <input type="submit" class="btn btn-primary" value="OK" :disabled="commandRunning">
              <button class="btn btn-default" @click.prevent="closeAddNodeModal()">
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </Modal>

    <div class="view-options">
      <div class="view-selector col-s-6 col-m-8 col-l-9">
        <label>
          <select @change="selected.view = $event.target.value">
            <option v-for="(id, view) in views" :key="id"
                    v-text="(view[0].toUpperCase() + view.slice(1)).replace('_', ' ')"
                    :selected="view === selected.view" :value="view" />
          </select>
        </label>
      </div>

      <div class="buttons col-s-6 col-m-4 col-l-3">
        <button class="btn btn-default" title="Create Scene" @click="addScene" v-if="selected.view === 'scenes'">
          <i class="fa fa-plus" />
        </button>

        <Dropdown title="Network commands" icon-class="fa fa-cog">
          <DropdownItem text="Network Info" :disabled="commandRunning" @input="networkInfoModalOpen" />
          <DropdownItem text="Start Network" :disabled="commandRunning" @input="startNetwork" />
          <DropdownItem text="Stop Network" :disabled="commandRunning" @input="stopNetwork" />
          <DropdownItem text="Add Node" :disabled="commandRunning"
            @input="openAddNodeModal()" v-if="selected.view === 'nodes'" />
          <DropdownItem text="Remove Node" :disabled="commandRunning" @input="removeNode"
                        v-if="selected.view === 'nodes'" />
          <DropdownItem text="Switch All On" :disabled="commandRunning" @input="switchAll(true)" />
          <DropdownItem text="Switch All Off" :disabled="commandRunning" @input="switchAll(false)" />
          <DropdownItem text="Cancel Command" :disabled="commandRunning" @input="cancelCommand" />
          <DropdownItem text="Kill Command" :disabled="commandRunning" @input="killCommand" />
          <DropdownItem text="Receive Configuration" :disabled="commandRunning" @input="receiveConfiguration" />
          <DropdownItem text="Create New Primary" :disabled="commandRunning" @input="createNewPrimary" />
          <DropdownItem text="Transfer Primary Role" :disabled="commandRunning" @input="transferPrimaryRole" />
          <DropdownItem text="Heal Network" :disabled="commandRunning" @input="healNetwork" />
          <DropdownItem text="Soft Reset" :disabled="commandRunning" @input="softReset" />
          <DropdownItem text="Hard Reset" :disabled="commandRunning" @input="hardReset" />
        </Dropdown>

        <button class="btn btn-default" title="Refresh Network" @click="refresh">
          <i class="fa fa-sync-alt" />
        </button>
      </div>
    </div>

    <div class="view-container">
      <div class="view nodes" v-if="selected.view === 'nodes'">
        <Loading v-if="loading.nodes" />
        <div class="no-items" v-else-if="!Object.keys(nodes || {}).length">
          <div class="empty">No nodes available on the network</div>
        </div>

        <Node v-for="(node, nodeId) in nodes" :key="nodeId" :node="node" :selected="selected.nodeId === nodeId"
              :plugin-name="pluginName" @select="onNodeClick(nodeId)" />
      </div>

      <div class="view groups" v-else-if="selected.view === 'groups'">
        <Loading v-if="loading.groups" />
        <div class="no-items" v-else-if="!Object.keys(groups || {}).length">
          <div class="empty">No groups available on the network</div>
        </div>

        <Group v-for="(group, groupId) in groups" :key="groupId" :group="group" :selected="selected.groupId === groupId"
               :nodes="groupId in groups ? groups[groupId].associations.map((node) => nodes[node]).
                     reduce((nodes, node) => {nodes[node.node_id] = node; return nodes}, {}) : {}"
               :owner="group.node_id != null ? nodes[group.node_id] : null" :plugin-name="pluginName"
               @select="selected.groupId = groupId === selected.groupId ? undefined : groupId"
               @open-add-nodes-to-group="$refs.addNodesToGroupModal.show()" />
      </div>

      <div class="view scenes" v-else-if="selected.view === 'scenes'">
        <Loading v-if="loading.scenes" />
        <div class="no-items" v-else-if="!Object.keys(scenes || {}).length">
          <div class="empty">No scenes configured on the network</div>
        </div>

        <div class="item scene" :class="{selected: selected.sceneId === sceneId}"
             v-for="(scene, sceneId) in scenes" :key="sceneId">
          <div class="row name header vertical-center" :class="{selected: selected.sceneId === sceneId}" v-text="scene.label"
               @click="selected.sceneId = sceneId === selected.sceneId ? undefined : sceneId" />

          <div class="params" v-if="selected.sceneId === sceneId">
            <div class="row">
              <div class="param-name">Scene ID</div>
              <div class="param-value" v-text="sceneId" />
            </div>

            <div class="row">
              <div class="param-name">Activate</div>
              <div class="param-value">
                <ToggleSwitch :value="false" @input="activateScene(sceneId)" />
              </div>
            </div>

            <div class="section values" v-if="Object.values(scene?.values)?.length">
              <div class="header">
                <div class="title">Values</div>
              </div>

              <div class="body">
                <div class="row" v-for="value in Object.values(scene.values)" :key="value.id_on_network">
                  <div class="param-name">
                    {{ nodes[value.node_id].name }} &#8680; {{ valuesMap[value.id_on_network].label }}
                  </div>
                  <div class="param-value">
                    <span v-text="value.data" />
                    <span class="buttons">
                    <button class="btn btn-default" title="Remove value"
                            @click="removeValueFromScene({sceneId: sceneId, valueId: value.id_on_network})">
                      <i class="fa fa-trash" />
                    </button>
                  </span>
                  </div>
                </div>
              </div>
            </div>

            <div class="section actions">
              <div class="header">
                <div class="title">Actions</div>
              </div>

              <div class="body">
                <div class="row" @click="removeScene(sceneId)">
                  <div class="param-name">Remove Scene</div>
                  <div class="param-value">
                    <i class="fa fa-trash" />
                  </div>
                </div>

                <div class="row" @click="renameScene(sceneId)">
                  <div class="param-name">Rename Scene</div>
                  <div class="param-value">
                    <i class="fa fa-edit" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="view values" v-else>
        <Loading v-if="loading.nodes" />
        <div class="no-items" v-else-if="!Object.keys(nodes || {}).length">
          <div class="empty">No nodes found on the network</div>
        </div>

        <div class="node-container" v-for="(node, nodeId) in nodes" :key="nodeId">
          <div class="item node"
               :class="{selected: selected.nodeId === nodeId}"
               v-if="selected.view === 'values' || Object.values(node.values).filter((value) => value.id_on_network in values[selected.view]).length > 0">
            <div class="row name header vertical-center" :class="{selected: selected.nodeId === nodeId}" v-text="node.name"
                 @click="onNodeClick(nodeId)"></div>

            <div class="params" v-if="selected.nodeId === nodeId">
              <div class="value-container" v-for="(value, valueId) in node.values" :key="valueId">
                <div class="value-display"
                     v-if="value.id_on_network && (selected.view === 'values' || value.id_on_network in values[selected.view])">
                  <Value :value="value" :node="node" :scenes="scenes" @add-to-scene="addValueToScene"
                         @remove-from-scene="removeValueFromScene" @refresh="refreshNodes" :plugin-name="pluginName" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Group from "@/components/panels/Zwave/Group";
import Node from "@/components/panels/Zwave/Node";
import Modal from "@/components/Modal";
import Alert from "@/components/elements/Alert";
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";
import Loading from "@/components/Loading";
import ToggleSwitch from "@/components/elements/ToggleSwitch";
import Value from "@/components/panels/Zwave/Value";
import mixin from "@/components/panels/Zwave/mixin";

export default {
  name: "Zwave",
  mixins: [mixin],
  components: {
    Alert,
    Dropdown,
    DropdownItem,
    Group,
    Loading,
    Modal,
    Node,
    ToggleSwitch,
    Value,
  },

  data() {
    return {
      status: {},
      views: {},
      nodes: {},
      groups: {},
      scenes: {},
      commandRunning: false,
      values: {
        switches: {},
        dimmers: {},
        sensors: {},
        battery_levels: {},
        power_levels: {},
        bulbs: {},
        doorlocks: {},
        usercodes: {},
        thermostats: {},
        protections: {},
      },
      selected: {
        view: 'nodes',
        nodeId: undefined,
        groupId: undefined,
        sceneId: undefined,
        valueId: undefined,
      },
      loading: {
        status: false,
        nodes: false,
        groups: false,
        scenes: false,
      },
    }
  },

  computed: {
    valuesMap() {
      const values = {}
      for (const node of Object.values(this.nodes)) {
        for (const value of Object.values(node.values)) {
          values[value.id_on_network] = value
        }
      }

      return values
    },
  },

  methods: {
    async refreshNodes() {
      this.loading.nodes = true
      try {
        this.nodes = await this.zrequest('get_nodes')
      } finally {
        this.loading.nodes = false
      }

      if (Object.keys(this.nodes || {}).length)
        this.views.values = true
    },

    async refreshGroups() {
      this.loading.groups = true

      try {
        this.groups = Object.values(await this.zrequest('get_groups'))
            .filter((group) => group.index)
            .reduce((groups, group) => {
              const id = group.group_id || group.index
              groups[id] = group
              return groups
            }, {})
      } finally {
        this.loading.groups = false
      }

      if (Object.keys(this.groups || {}).length)
        this.views.groups = true
    },

    async refreshScenes() {
      this.loading.scenes = true

      try {
        this.scenes = Object.values(await this.zrequest('get_scenes'))
            .filter((scene) => scene.scene_id)
            .reduce((scenes, scene) => {
              scenes[scene.scene_id] = scene
              return scenes
            }, {})
      } finally {
        this.loading.scenes = false
      }

      if (Object.keys(this.scenes || {}).length)
        this.views.values = true
    },

    async refreshValues(type) {
      this.loading.values = true

      try {
        this.values[type] = Object.values(await this.zrequest('get_' + type))
            .filter((item) => item.id_on_network)
            .reduce((values, value) => {
              values[value.id_on_network] = true
              return values
            }, {})
      } finally {
        this.loading.values = false
      }

      if (Object.keys(this.values[type]).length)
        this.views[type] = true
    },

    async refreshStatus() {
      this.loading.status = true
      try {
        this.status = await this.zrequest('controller_status')
      } finally {
        this.loading.status = false
      }
    },

    refresh() {
      this.views = {
        nodes: true,
        scenes: true,
      }

      this.refreshNodes()
      this.refreshGroups()
      this.refreshScenes()
      this.refreshValues('switches')
      this.refreshValues('dimmers')
      this.refreshValues('sensors')
      this.refreshValues('bulbs')
      this.refreshValues('doorlocks')
      this.refreshValues('usercodes')
      this.refreshValues('thermostats')
      this.refreshValues('protections')
      this.refreshValues('battery_levels')
      this.refreshValues('power_levels')
      this.refreshValues('node_config')
      this.refreshStatus()
    },

    async addScene() {
      let name = prompt('Scene name')
      if (name?.length)
        name = name.trim()
      if (!name?.length)
        return

      this.commandRunning = true
      try {
        await this.zrequest('create_scene', {label: name})
        await this.refreshScenes()
      } finally {
        this.commandRunning = false
      }
    },

    async removeScene(sceneId) {
      if (!confirm('Are you sure that you want to delete this scene?'))
        return

      this.commandRunning = true
      try {
        await this.zrequest('remove_scene', {scene_id: sceneId})
        await this.refreshScenes()
      } finally {
        this.commandRunning = false
      }
    },

    onNodeUpdate(event) {
      this.nodes[event.node.node_id] = event.node
      if (event.value)
        this.nodes[event.node.node_id].values[event.value.id_on_network] = event.value
    },

    onNodeClick(nodeId) {
      this.selected.nodeId = nodeId === this.selected.nodeId ? undefined : nodeId
    },

    networkInfoModalOpen() {
      this.refreshStatus()
      this.$refs.networkInfoModal.show()
    },

    onCommandEvent(event) {
      if (event.error && event.error.length) {
        this.notify({
          text: event.state_description + ': ' + event.error_description,
          error: true,
        })
      }
    },

    resetAddNodeModal() {
      [...this.$refs.addNodeModal.$el.querySelectorAll('.fields input')].forEach(
          (el) => { el.value = (el.attributes.name.value === 'timeout') ? 30 : '' }
      )
    },

    openAddNodeModal() {
      this.resetAddNodeModal()
      this.$refs.addNodeModal.show()
    },

    closeAddNodeModal() {
      this.resetAddNodeModal()
      this.$refs.addNodeModal.close()
    },

    async addNode() {
      const form = this.$refs.addNodeForm
      const name = form.querySelector('input[name=name]').value?.trim()
      const location = form.querySelector('input[name=location]').value?.trim()
      const timeout = parseInt(
        form.querySelector('input[name=location]').value?.trim() || 30
      )

      if (!name?.length) {
        this.$refs.noNodeNameModal.show()
        return
      }

      this.commandRunning = true
      try {
        await this.zrequest('add_node', {
          name: name,
          location: location,
          timeout: timeout,
        })

        this.closeAddNodeModal()
      } finally {
        this.commandRunning = false
      }

      await this.refreshNodes()
    },

    async addToGroup(nodeId, groupId) {
      this.commandRunning = true
      try {
        await this.zrequest('add_node_to_group', {
          node_id: nodeId,
          group_index: groupId,
        })
      } finally {
        this.commandRunning = false
      }

      await this.refreshGroups()
    },

    async removeNode() {
      this.commandRunning = true
      try {
        await this.zrequest('remove_node')
      } finally {
        this.commandRunning = false
      }

      await this.refreshNodes()
    },

    async removeValueFromScene(event) {
      if (!confirm('Are you sure that you want to remove this value from the scene?'))
        return

      this.commandRunning = true
      try {
        await this.zrequest('scene_remove_value', {
          id_on_network: event.valueId,
          scene_id: event.sceneId,
        })
      } finally {
        this.commandRunning = false
      }

      await this.refreshScenes()
    },

    async renameScene(sceneId) {
      const scene = this.scenes[sceneId]
      let name = prompt('New name', scene.label)
      if (name)
        name = name.trim()
      if (!name?.length || name === scene.label)
        return

      this.commandRunning = true
      try {
        await this.zrequest('set_scene_label', {
          new_label: name,
          scene_id: sceneId,
        })
      } finally {
        this.commandRunning = false
      }

      await this.refreshScenes()
    },

    async startNetwork() {
      this.commandRunning = true
      try {
        await this.zrequest('start_network')
      } finally {
        this.commandRunning = false
      }
    },

    async stopNetwork() {
      this.commandRunning = true
      try {
        await this.zrequest('stop_network')
      } finally {
        this.commandRunning = false
      }
    },

    async switchAll(state) {
      this.commandRunning = true
      try {
        await this.zrequest('switch_all', {state: state})
        this.refresh()
      } finally {
        this.commandRunning = false
      }
    },

    async cancelCommand() {
      this.commandRunning = true
      try {
        await this.zrequest('cancel_command')
      } finally {
        this.commandRunning = false
      }
    },

    async killCommand() {
      this.commandRunning = true
      try {
        await this.zrequest('kill_command')
      } finally {
        this.commandRunning = false
      }
    },

    async receiveConfiguration() {
      this.commandRunning = true
      try {
        await this.zrequest('receive_configuration')
      } finally {
        this.commandRunning = false
      }

      this.refresh()
    },

    async createNewPrimary() {
      this.commandRunning = true
      try {
        await this.zrequest('create_new_primary')
      } finally {
        this.commandRunning = false
      }

      this.refresh()
    },

    async transferPrimaryRole() {
      this.commandRunning = true
      try {
        await this.zrequest('transfer_primary_role')
      } finally {
        this.commandRunning = false
      }

      this.refresh()
    },

    async healNetwork() {
      this.commandRunning = true
      try {
        await this.zrequest('heal')
      } finally {
        this.commandRunning = false
      }

      this.refresh()
    },

    async softReset() {
      if (!confirm("Are you sure that you want to do a device soft reset? This won't lose network information"))
        return

      await this.zrequest('soft_reset')
    },

    async hardReset() {
      if (!confirm("Are you sure that you want to do a device soft reset? All network information will be LOST!"))
        return

      await this.zrequest('hard_reset')
    },

    async activateScene(sceneId) {
      this.commandRunning = true
      try {
        await this.zrequest('activate_scene', {scene_id: sceneId})
      } finally {
        this.commandRunning = false
      }
    },

    async addValueToScene(event) {
      this.commandRunning = true
      try {
        await this.zrequest('scene_add_value', {
          id_on_network: event.valueId,
          scene_id: event.sceneId,
          data: this.valuesMap[event.valueId].data,
        })
      } finally {
        this.commandRunning = false
      }

      this.refresh()
    },
  },

  mounted() {
    this.refresh()

    this.subscribe(this.refreshGroups, 'on-zwave-node-group-event',
        'platypush.message.event.zwave.ZwaveNodeGroupEvent')

    this.subscribe(this.refreshScenes, 'on-zwave-node-scene-event',
        'platypush.message.event.zwave.ZwaveNodeSceneEvent')

    this.subscribe(this.refreshNodes, 'on-zwave-node-removed-event',
        'platypush.message.event.zwave.ZwaveNodeRemovedEvent')

    this.subscribe(this.onCommandEvent, 'on-zwave-command-event',
        'platypush.message.event.zwave.ZwaveCommandEvent')

    this.subscribe(this.refreshStatus, 'on-zwave-network-event',
        'platypush.message.event.zwave.ZwaveNetworkReadyEvent',
        'platypush.message.event.zwave.ZwaveNetworkStoppedEvent',
        'platypush.message.event.zwave.ZwaveNetworkErrorEvent',
        'platypush.message.event.zwave.ZwaveNetworkResetEvent')

    this.subscribe(this.onNodeUpdate, 'on-zwave-node-update-event',
        'platypush.message.event.zwave.ZwaveNodeEvent',
        'platypush.message.event.zwave.ZwaveNodeAddedEvent',
        'platypush.message.event.zwave.ZwaveNodeRenamedEvent',
        'platypush.message.event.zwave.ZwaveNodeReadyEvent',
        'platypush.message.event.zwave.ZwaveValueAddedEvent',
        'platypush.message.event.zwave.ZwaveValueChangedEvent',
        'platypush.message.event.zwave.ZwaveValueRemovedEvent',
        'platypush.message.event.zwave.ZwaveValueRefreshedEvent')
  },

  unmounted() {
    [
      'on-zwave-node-group-event', 'on-zwave-node-scene-event', 'on-zwave-node-removed-event', 'on-zwave-command-event',
      'on-zwave-network-event', 'on-zwave-node-update-event'
    ].forEach((eventType) => this.unsubscribe(eventType))
  },
}
</script>

<style lang="scss">
@import "common";

.zwave-container {
  width: 100%;
  height: 100%;
  padding: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: auto;

  .view-options {
    display: flex;
    width: 100%;
    height: $header-height;
    justify-content: space-between;
    align-items: center;
    padding: 0;
    background: $header-bg;
    border-bottom: $default-border-2;
    box-shadow: $border-shadow-bottom;

    .view-selector {
      display: inline-flex;
      padding-left: .5em;

      label {
        width: 100%;
      }
    }

    select {
      width: 100%;
    }

    .buttons {
      display: inline-flex;
      margin: 0 !important;
      justify-content: flex-end;

      button {
        border: none;
        background: none;
      }
    }
  }

  .group-add {
    margin: -2em;
    min-width: 20em;
    padding-bottom: 1em;
  }

  .network-info {
    margin: -1em;
  }

  .add-node-form, .fields {
    display: flex;
    flex-direction: column;
    justify-content: center;

    input {
      margin: 0.5em;
    }

    .buttons {
      box-shadow: 0 -1px $default-shadow-color;
      margin-top: 0.75em;
      padding-top: 0.75em;
      justify-content: right;
    }
  }
}
</style>

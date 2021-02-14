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
                   v-for="node in Object.values(nodes || {}).filter((n) => groups[selected.groupId].associations.indexOf(n.node_id) < 0)">
                <div class="param-name" v-text="node.name"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Modal>

    <div class="view-options">
      <div class="view-selector col-s-9 col-m-10 col-l-11">
        <label>
          <select @change="selected.view = $event.target.value">
            <option v-for="(id, view) in views"
                    v-text="(view[0].toUpperCase() + view.slice(1)).replace('_', ' ')"
                    :key="id"
                    :selected="view === selected.view"
                    :value="view">
            </option>
          </select>
        </label>
      </div>

      <div class="buttons">
        <button class="btn btn-default" title="Add node" v-if="selected.view === 'nodes'" @click="addNode"
                :disabled="commandRunning">
          <i class="fa fa-plus" />
        </button>

        <button class="btn btn-default" title="Remove node" v-if="selected.view === 'nodes'" @click="removeNode"
                :disabled="commandRunning">
          <i class="fa fa-minus" />
        </button>

        <button class="btn btn-default" title="Add scene" v-if="selected.view === 'scenes'" @click="addScene"
                :disabled="commandRunning">
          <i class="fa fa-plus" />
        </button>

        <button class="btn btn-default" title="Network info" @click="networkInfoModalOpen">
          <i class="fa fa-info" />
        </button>

        <Dropdown title="Network commands" icon-class="fa fa-cog">
          <DropdownItem text="Start Network" :disabled="commandRunning" @click="startNetwork" />
          <DropdownItem text="Stop Network" :disabled="commandRunning" @click="stopNetwork" />
          <DropdownItem text="Switch All On" :disabled="commandRunning" @click="switchAll(true)" />
          <DropdownItem text="Switch All Off" :disabled="commandRunning" @click="switchAll(false)" />
          <DropdownItem text="Cancel Command" :disabled="commandRunning" @click="cancelCommand" />
          <DropdownItem text="Kill Command" :disabled="commandRunning" @click="killCommand" />
          <DropdownItem text="Receive Configuration" :disabled="commandRunning" @click="receiveConfiguration" />
          <DropdownItem text="Create New Primary" :disabled="commandRunning" @click="createNewPrimary" />
          <DropdownItem text="Transfer Primary Role" :disabled="commandRunning" @click="transferPrimaryRole" />
          <DropdownItem text="Heal Network" :disabled="commandRunning" @click="healNetwork" />
          <DropdownItem text="Soft Reset" :disabled="commandRunning" @click="softReset" />
          <DropdownItem text="Hard Reset" :disabled="commandRunning" @click="hardReset" />
        </Dropdown>

        <button class="btn btn-default" title="Refresh network" @click="refresh">
          <i class="fa fa-sync-alt" />
        </button>
      </div>
    </div>

    <div class="view nodes" v-if="selected.view === 'nodes'">
      <Loading v-if="loading.nodes" />
      <div class="no-items" v-else-if="!Object.keys(nodes || {}).length">
        <div class="empty">No nodes available on the network</div>
      </div>

      <Node v-for="(node, nodeId) in nodes" :key="nodeId" :node="node" :selected="selected.nodeId === nodeId"
            @select="onNodeClick(nodeId)" />
    </div>

    <div class="view groups" v-else-if="selected.view === 'groups'">
      <Loading v-if="loading.groups" />
      <div class="no-items" v-else-if="!Object.keys(groups || {}).length">
        <div class="empty">No groups available on the network</div>
      </div>

      <Group v-for="(group, groupId) in groups" :key="groupId" :group="group" :selected="selected.groupId === groupId"
             :nodes="groupId in groups ? groups[groupId].associations.map((node) => nodes[node]).
                     reduce((nodes, node) => {nodes[node.node_id] = node; return nodes}, {}) : {}"
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
        <div class="row name vertical-center" :class="{selected: selected.sceneId === sceneId}" v-text="scene.label"
             @click="selected.sceneId = sceneId === selected.sceneId ? undefined : sceneId" />

        <div class="params" v-if="selected.sceneId === sceneId">
          <div class="row">
            <div class="param-name">Activate</div>
            <div class="param-value">
              <ToggleSwitch :value="false" @input="activateScene(sceneId)" />
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
                  <i class="fa fa-trash"></i>
                </div>
              </div>

              <div class="row" @click="renameScene(sceneId)">
                <div class="param-name">Rename Scene</div>
                <div class="param-value">
                  <i class="fa fa-edit"></i>
                </div>
              </div>
            </div>
          </div>

          <div class="section values" v-if="scene.values?.length">
            <div class="value-container" v-for="(value, valueId) in valuesMap" :key="valueId">
              <div class="value-display"
                   v-if="value.valueId && value.valueId in scenes.values[sceneId]" :scenes="scenes">
                <Value :value="value" :node="node" :sceneId="sceneId" @add-to-scene="addValueToScene"
                       @remove-from-scene="removeValueFromScene" @refresh="refreshNodes" />
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
          <div class="row name vertical-center" :class="{selected: selected.nodeId === nodeId}" v-text="node.name"
               @click="onNodeClick(nodeId)"></div>

          <div class="params" v-if="selected.nodeId === nodeId">
            <div class="value-container" v-for="(value, valueId) in node.values" :key="valueId">
              <div class="value-display"
                   v-if="valueId && (selected.view === 'values' || value.valueId in values[selected.view])">
                <Value :value="value" :node="node" :scenes="scenes" @add-to-scene="addValueToScene"
                       @remove-from-scene="removeValueFromScene" @refresh="refreshNodes" />
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
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";
import Loading from "@/components/Loading";
import ToggleSwitch from "@/components/elements/ToggleSwitch";
import Value from "@/components/panels/Zwave/Value";
import Utils from "@/Utils";

export default {
  name: "Zwave",
  components: {Value, ToggleSwitch, Loading, DropdownItem, Dropdown, Modal, Group, Node},
  mixins: [Utils],

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
        this.nodes = await this.request('zwave.get_nodes')
      } finally {
        this.loading.nodes = false
      }

      if (Object.keys(this.nodes || {}).length)
        this.views.values = true
    },

    async refreshGroups() {
      this.loading.groups = true

      try {
        this.groups = Object.values(await this.request('zwave.get_groups'))
            .filter((group) => group.index)
            .reduce((groups, group) => {
              groups[group.index] = group
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
        this.scenes = Object.values(await this.request('zwave.get_scenes'))
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
        this.values[type] = Object.values(await this.request('zwave.get_' + type))
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
        this.status = await this.request('zwave.status')
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
        await this.request('zwave.create_scene', {label: name})
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
        await this.request('zwave.remove_scene', {scene_id: sceneId})
        await this.refreshScenes()
      } finally {
        this.commandRunning = false
      }
    },

    onNodeUpdate(event) {
      this.nodes[event.node.node_id] = event.node
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

    async addNode() {
      this.commandRunning = true
      try {
        await this.request('zwave.add_node')
      } finally {
        this.commandRunning = false
      }

      await this.refreshNodes()
    },

    async addToGroup(nodeId, groupId) {
      this.commandRunning = true
      try {
        await this.request('zwave.add_node_to_group', {
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
        await this.request('zwave.remove_node')
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
        await this.request('zwave.scene_remove_value', {
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
        await this.request('zwave.set_scene_label', {
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
        await this.request('zwave.start_network')
      } finally {
        this.commandRunning = false
      }
    },

    async stopNetwork() {
      this.commandRunning = true
      try {
        await this.request('zwave.stop_network')
      } finally {
        this.commandRunning = false
      }
    },

    async switchAll(state) {
      this.commandRunning = true
      try {
        await this.request('zwave.switch_all', {state: state})
        this.refresh()
      } finally {
        this.commandRunning = false
      }
    },

    async cancelCommand() {
      this.commandRunning = true
      try {
        await this.request('zwave.cancel_command')
      } finally {
        this.commandRunning = false
      }
    },

    async killCommand() {
      this.commandRunning = true
      try {
        await this.request('zwave.kill_command')
      } finally {
        this.commandRunning = false
      }
    },

    async setControllerName() {
      let name = prompt('Controller name')
      if (name?.length)
        name = name.trim()
      if (!name?.length)
        return

      this.commandRunning = true
      try {
        await this.request('zwave.set_controller_name', {name: name})
      } finally {
        this.commandRunning = false
      }

      this.refresh()
    },

    async receiveConfiguration() {
      this.commandRunning = true
      try {
        await this.request('zwave.receive_configuration')
      } finally {
        this.commandRunning = false
      }

      this.refresh()
    },

    async createNewPrimary() {
      this.commandRunning = true
      try {
        await this.request('zwave.create_new_primary')
      } finally {
        this.commandRunning = false
      }

      this.refresh()
    },

    async transferPrimaryRole() {
      this.commandRunning = true
      try {
        await this.request('zwave.transfer_primary_role')
      } finally {
        this.commandRunning = false
      }

      this.refresh()
    },

    async healNetwork() {
      this.commandRunning = true
      try {
        await this.request('zwave.heal')
      } finally {
        this.commandRunning = false
      }

      this.refresh()
    },

    async softReset() {
      if (!confirm("Are you sure that you want to do a device soft reset? This won't lose network information"))
        return

      await this.request('zwave.soft_reset')
    },

    async hardReset() {
      if (!confirm("Are you sure that you want to do a device soft reset? All network information will be LOST!"))
        return

      await this.request('zwave.hard_reset')
    },

    async activateScene(sceneId) {
      this.commandRunning = true
      try {
        await this.request('zwave.activate_scene', {scene_id: sceneId})
      } finally {
        this.commandRunning = false
      }
    },

    async addValueToScene(event) {
      if (!this.selected.valueId)
        return

      this.commandRunning = true
      try {
        await this.request('zwave.scene_add_value', {
          id_on_network: event.valueId,
          scene_id: event.sceneId,
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

<style lang="scss" scoped>
@import "common";

.zwave-container {
  width: 100%;
  height: 100%;
  padding: 0 .5em;
  background: $container-bg;
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

    .view-selector {
      display: inline-flex;
    }

    select {
      width: 100%;
      border-radius: 1em;
    }
  }
}
</style>

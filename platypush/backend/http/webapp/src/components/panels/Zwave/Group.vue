<template>
  <div class="item group" :class="{selected: selected}">
    <div class="row name header vertical-center" :class="{selected: selected}" v-text="group.label"
         @click="$emit('select', group.index)" />

    <div class="params" v-if="selected">
      <div class="section nodes">
        <div class="header">
          <div class="title col-10">Nodes</div>
          <div class="buttons col-2">
            <button class="btn btn-default" title="Add to group" @click="$emit('open-add-nodes-to-group', group.index)"
                    v-if="!group.max_associations || Object.keys(nodes || {}).length < group.max_associations">
              <i class="fa fa-plus" />
            </button>
          </div>
        </div>

        <div class="body">
          <div class="row" v-for="(node, i) in nodes" :key="i">
            <div class="col-10" v-text="node.name?.length ? node.name : `<Node ${node.node_id}>`" />
            <div class="buttons col-2">
              <button class="btn btn-default" title="Remove from group" :disabled="commandRunning"
                      @click="removeFromGroup(node.node_id)">
                <i class="fa fa-trash" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="section config">
        <div class="header">
          <div class="title">Parameters</div>
        </div>

        <div class="body">
          <div class="row">
            <div class="param-name">Index</div>
            <div class="param-value" v-text="group.index"></div>
          </div>

          <div class="row">
            <div class="param-name">Max associations</div>
            <div class="param-value" v-text="group.max_associations"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Utils from "@/Utils";

export default {
  name: "Group",
  emits: ['select', 'open-add-nodes-to-group'],
  mixins: [Utils],

  props: {
    group: {
      type: Object,
      required: true,
    },
    nodes: {
      type: Object,
      default: () => { return {} },
    },
    selected: {
      type: Boolean,
      default: false,
    }
  },

  data() {
    return {
      commandRunning: false,
    }
  },

  methods: {
    async removeFromGroup(nodeId) {
      if (!confirm('Are you sure that you want to remove this node from ' + this.group.label + '?'))
        return

      this.commandRunning = true
      try {
        await this.request('zwave.remove_node_from_group', {
          node_id: nodeId,
          group_index: this.group.index,
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

<template>
  <div class="item group" :class="{selected: selected}">
    <div class="row name header vertical-center" :class="{selected: selected}" v-text="group.label"
         @click="$emit('select', group.index)" />

    <div class="params" v-if="selected">
      <div class="section owner" v-if="owner && Object.keys(owner).length">
        <div class="header">
          <div class="title">Owner</div>
        </div>

        <div class="body">
          <div class="row" v-text="owner.name" />
        </div>
      </div>

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
import mixin from "@/components/panels/Zwave/mixin";

export default {
  name: "Group",
  emits: ['select', 'open-add-nodes-to-group'],
  mixins: [mixin],

  props: {
    group: {
      type: Object,
      required: true,
    },
    owner: {
      type: Object,
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
      const args = {
        node_id: nodeId,
      }

      if (this.group.group_id != null)
        args.group_id = this.group.group_id
      else
        args.group_index = this.group.index

      try {
        await this.zrequest('remove_node_from_group', args)
      } finally {
        this.commandRunning = false
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import "common";

.section.nodes {
  .header, .row {
    position: relative;

    .buttons {
      position: absolute;
      right: 0;
      display: flex;
      justify-content: right;
    }
  }
}
</style>

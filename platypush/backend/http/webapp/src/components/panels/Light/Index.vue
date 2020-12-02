<template>
  <div class="plugin lights-plugin">
    <div class="panel" v-if="selectedGroup == null && groups && Object.keys(groups).length">
      <Groups :groups="groups" :loading-groups="loadingGroups" @select="selectedGroup = $event" @toggle="toggleGroup" />
    </div>
    <div class="panel" v-else>
      <Group :group="groups[selectedGroup]" :lights="displayedLights" @close="closeGroup" />
    </div>
  </div>
</template>

<script>
import Utils from "@/Utils";
import Panel from "@/components/panels/Panel";
import Groups from "@/components/Light/Groups";
import Group from "@/components/Light/Group";

/**
 * Generic component for light plugins panels.
 */
export default {
  name: "Light",
  components: {Group, Groups},
  mixins: [Utils, Panel],
  emits: ['group-toggle'],

  props: {
    lights: {
      type: Object,
    },

    groups: {
      type: Object,
    },

    scenes: {
      type: Object,
    },

    animations: {
      type: Object,
    },

    loadingLights: {
      type: Object,
      default: () => {},
    },

    loadingGroups: {
      type: Object,
      default: () => {},
    },

    pluginName: {
      type: String,
    },

    initialGroup: {
      type: [Number, String],
    },
  },

  data() {
    return {
      selectedGroup: null,
      initialized: false,
    }
  },

  computed: {
    displayedLights() {
      const selectedGroup = this.selectedGroup || this.initialGroup
      if (selectedGroup == null)
        return this.lights

      return this.groups[selectedGroup].lights.reduce((lights, lightId) => {
        lights[lightId] = this.lights[lightId]
        return lights
      }, {})
    },
  },

  methods: {
    initSelectedGroup() {
      const self = this
      const unwatch = this.$watch(() => self.initialGroup, (newVal) => {
        if (!self.initialized) {
          self.initialized = true
          unwatch()
          if (self.selectedGroup == null && newVal != null) {
            self.selectedGroup = self.initialGroup
          }
        }
      })
    },

    closeGroup() {
      this.selectedGroup = null
    },

    toggleGroup(group) {
      this.$emit('group-toggle', group)
    },
  },

  mounted() {
    this.initSelectedGroup()
  },
}
</script>

<style lang="scss" scoped>
.plugin {
  width: 100%;
  height: 100%;
  display: flex;
}

.panel {
  width: 100%;
  height: 100%;
  box-shadow: none;
  overflow: auto;
}
</style>

<style lang="scss">
.lights-plugin {
  .menu-panel {
    ul {
      li:not(.header) {
        padding: 1.5em 1em;
      }
    }
  }
}
</style>
<template>
  <div class="plugin lights-plugin">
    <div class="panel" v-if="selectedGroup == null && groups && Object.keys(groups).length">
      <Groups :groups="groups" :loading-groups="loadingGroups" :color-converter="colorConverter"
              @select="selectedGroup = $event" @toggle="$emit('group-toggle', $event)" />
    </div>
    <div class="panel" v-else>
      <Group :group="groups[selectedGroup]" :lights="displayedLights" :scenes="scenesByGroup[selectedGroup]"
             :color-converter="colorConverter" @close="closeGroup" @light-toggle="$emit('light-toggle', $event)"
             @group-toggle="$emit('group-toggle', $event)" @set-light="$emit('set-light', $event)"
             @set-group="$emit('set-group', {groupId: selectedGroup, value: $event})"
             @select-scene="$emit('select-scene', {groupId: selectedGroup, sceneId: $event})" />
    </div>
  </div>
</template>

<script>
import Utils from "@/Utils";
import Panel from "@/components/panels/Panel";
import Groups from "@/components/Light/Groups";
import Group from "@/components/Light/Group";
import {ColorConverter} from "@/components/panels/Light/color";

/**
 * Generic component for light plugins panels.
 */
export default {
  name: "Light",
  components: {Group, Groups},
  mixins: [Utils, Panel],
  emits: ['group-toggle', 'light-toggle', 'set-light', 'set-group', 'select-scene'],

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

    colorConverter: {
      type: Object,
      default: () => new ColorConverter(),
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

    lightsByGroup() {
      if (!this.groups)
        return {}

      const self = this
      return Object.entries(this.groups).reduce((obj, [groupId, group]) => {
        obj[groupId] = group.lights.map((lightId) => self.lights[lightId])
        return obj
      }, {})
    },

    groupsByLight() {
      if (!this.groups)
        return {}

      return Object.entries(this.groups).reduce((obj, [groupId, group]) => {
        group.lights.forEach((lightId) => {
          if (!obj[lightId])
            obj[lightId] = {}
          obj[lightId][groupId] = group
        })

        return obj
      }, {})
    },

    scenesByGroup() {
      if (!this.scenes)
        return {}

      const self = this
      return Object.entries(this.scenes).reduce((obj, [sceneId, scene]) => {
        scene.lights.forEach((lightId) => {
          Object.keys(self.groupsByLight[lightId]).forEach((groupId) => {
            if (!obj[groupId])
              obj[groupId] = {}

            obj[groupId][sceneId] = scene
          })
        })

        return obj
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
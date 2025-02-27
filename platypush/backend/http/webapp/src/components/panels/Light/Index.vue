<template>
  <div class="plugin lights-plugin">
    <div class="panel">
      <div class="groups lights-container" v-if="selectedGroup == null && Object.keys(groups || {}).length">
        <Groups :groups="groups"
                :loading-groups="loadingGroups"
                :color-converter="colorConverter"
                @select="selectedGroup = $event"
                @toggle="$emit('group-toggle', $event)" />
      </div>

      <div class="lights-container ungrouped-lights"
           v-if="Object.keys(ungroupedLights || {}).length && selectedGroup == null">
          <Group :group="ungroupedLights"
                 :lights="ungroupedLights"
                 :scenes="scenesByGroup[selectedGroup]"
                 :color-converter="colorConverter" 
                 :animations="animationsByGroup[selectedGroup]"
                 :with-back-button="false"
                 title="Ungrouped Lights"
                 @close="selectedGroup = null"
                 @light-toggle="$emit('light-toggle', $event)"
                 @select-scene="$emit('select-scene', {groupId: selectedGroup, sceneId: $event})"
                 @set-light="$emit('set-light', $event)"
                 @start-animation="$emit('start-animation', $event)"
                 @stop-animation="$emit('stop-animation', $event)" />
      </div>

      <div class="group" v-if="groups?.[selectedGroup]">
        <Group :group="groups[selectedGroup]"
               :lights="displayedLights"
               :scenes="scenesByGroup[selectedGroup]"
               :color-converter="colorConverter" 
               :animations="animationsByGroup[selectedGroup]"
               @close="selectedGroup = null"
               @group-toggle="$emit('group-toggle', $event)"
               @light-toggle="$emit('light-toggle', $event)"
               @select-scene="$emit('select-scene', {groupId: selectedGroup, sceneId: $event})"
               @set-group="$emit('set-group', {groupId: selectedGroup, value: $event})"
               @set-light="$emit('set-light', $event)"
               @start-animation="$emit('start-animation', $event)"
               @stop-animation="$emit('stop-animation', $event)" />
      </div>
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
  mixins: [Utils, Panel],
  components: {
    Group,
    Groups,
  },

  emits: [
    'group-toggle',
    'light-changed',
    'light-toggle',
    'refresh',
    'select-scene',
    'set-group',
    'set-light',
    'start-animation',
    'stop-animation',
  ],

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

    ungroupedLights() {
      return Object.keys(this.lights || {})
        .filter((lightId) => !this.groupsByLight[lightId])
        .reduce((obj, lightId) => {
          obj[lightId] = this.lights[lightId]
          return obj
        }, {})
    },

    scenesByGroup() {
      if (!this.scenes)
        return {}

      const self = this
      return Object.entries(this.scenes).reduce((obj, [sceneId, scene]) => {
        scene.lights.forEach((lightId) => {
          if (!self.groupsByLight[lightId]) {
            if (!obj[-1])
              obj[-1] = {}
            obj[-1][sceneId] = scene
            return
          }

          Object.keys(self.groupsByLight[lightId]).forEach((groupId) => {
            if (!obj[groupId])
              obj[groupId] = {}
            obj[groupId][sceneId] = scene
          })
        })

        return obj
      }, {})
    },

    animationsByGroup() {
      const self = this
      const animations = Object.entries(this.animations?.groups || {}).reduce((obj, [groupId, animation]) => {
        obj[groupId] = {}
        if (animation)
          obj[groupId][null] = animation    // lgtm [js/implicit-operand-conversion]

        return obj
      }, {})

      return {
        ...animations,
        ...Object.entries(this.animations?.lights || {}).reduce((obj, [lightId, animation]) => {
          const group = Object.values(self.groupsByLight[lightId] || {})?.[0]
          if (group) {
            if (animation && group.id != null) {
              if (!obj[group.id])
                obj[group.id] = {}
              obj[group.id][lightId] = animation
            }
          } else {
            if (!obj[-1])
              obj[-1] = {}
            obj[-1][lightId] = animation
          }

          return obj
        }, {})
      }
    }
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

    refresh() {
      this.$emit('refresh')
    },

    onLightChange(event) {
      if (event.plugin_name !== this.pluginName)
        return

      if (!this.lights[event.light_id]) {
        this.refresh()
        return
      }

      const state = {...event}
      const lightId = state.light_id
      delete state.light_id
      delete state.type
      delete state.plugin_name

      this.$emit('light-changed', {
        id: lightId,
        state: state,
      })
    },

    onAnimationChange(event) {
      if (event.plugin_name !== this.pluginName)
        return

      this.refresh()
    },
  },

  mounted() {
    this.subscribe(this.onLightChange, 'on-light-change',
        'platypush.message.event.light.LightStatusChangeEvent')
    this.subscribe(this.onAnimationChange, 'on-animation-change',
        'platypush.message.event.light.LightAnimationStartedEvent',
        'platypush.message.event.light.LightAnimationStoppedEvent')

    this.initSelectedGroup()
  },

  unmounted() {
    this.unsubscribe('on-light-change')
    this.unsubscribe('on-animation-change')
  },
}
</script>

<style lang="scss" scoped>
.plugin {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.panel {
  width: 100%;
  height: 100%;
  box-shadow: none;
  overflow: auto;
}
</style>

<style lang="scss">
@import "@/components/Light/groups.scss";

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

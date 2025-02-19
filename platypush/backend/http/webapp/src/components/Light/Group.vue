<template>
  <div class="light-group-container">
    <MenuPanel>
      <div class="panel-row header">
        <div class="col-3" v-if="group">
          <button class="back-btn" title="Back" @click="close" v-if="withBackButton">
            <i class="fas fa-chevron-left" />
          </button>
        </div>

        <div class="col-6 name" :class="{selected: selectedView === 'group'}"
             v-text="groupName" @click="selectedView = selectedView === 'group' ? null : 'group'" />

        <div class="col-3 pull-right" v-if="group">
          <ToggleSwitch :value="anyLightsOn" @input="$emit('group-toggle', group)" />
        </div>
      </div>

      <div class="no-lights" v-if="!lights || !Object.keys(lights).length">
        No lights found
      </div>

      <div class="lights-view" v-else>
        <div class="row view-selector">
          <button :class="{selected: selectedView === 'lights'}" :title="title" @click="selectedView = 'lights'">
            <i class="icon fas fa-lightbulb" />
          </button>
          <button :class="{selected: selectedView === 'scenes'}" title="Scenes" @click="selectedView = 'scenes'">
            <i class="icon far fa-image" />
          </button>
          <button :class="{selected: selectedView === 'animate'}" title="Animate" @click="selectedView = 'animate'">
            <i class="icon fas fa-video" />
          </button>
        </div>

        <div class="view fade-in" v-if="selectedView === 'lights'">
          <keep-alive>
            <div class="panel-row row" :class="{expanded: light.id === selectedLight}"
                 v-for="(light, id) in lightsSorted" :key="id"
                 @click="selectedLight = selectedLight === light.id ? null : light.id">
              <Light :light="light" :group="group" :collapsed="light.id !== selectedLight"
                     :color-converter="colorConverter" @toggle="$emit('light-toggle', light)"
                     @set-light="$emit('set-light', {light: light, value: $event})" />
            </div>
          </keep-alive>
        </div>

        <div class="view fade-in" v-else-if="selectedView === 'scenes'">
          <keep-alive>
            <div class="panel-row row" :class="{selected: scene.id === selectedScene}"
                 v-for="(scene, id) in scenesSorted" :key="id" @click="onSceneSelected(scene.id)">
              <Scene :scene="scene" :group="group" />
            </div>
          </keep-alive>
        </div>

        <div class="view group-controls fade-in" v-else-if="selectedView === 'group'">
          <keep-alive>
            <Controls :group="group" :lights="lights" :color-converter="colorConverter"
                      @set-group="$emit('set-group', $event)" />
          </keep-alive>
        </div>

        <div class="view group-controls fade-in" v-else-if="selectedView === 'animate'">
          <keep-alive>
            <Animate :group="group" :lights="lights" :color-converter="colorConverter" :running-animations="animations"
                     @start="$emit('start-animation', $event)" @stop="$emit('stop-animation', $event)" />
          </keep-alive>
        </div>
      </div>
    </MenuPanel>
  </div>
</template>

<script>
import Light from "@/components/Light/Light";
import Scene from "@/components/Light/Scene";
import Controls from "@/components/Light/Controls";
import MenuPanel from "@/components/MenuPanel";
import ToggleSwitch from "@/components/elements/ToggleSwitch";
import {ColorConverter} from "@/components/panels/Light/color";
import Animate from "@/components/Light/Animate";

export default {
  name: "Group",
  emits: ['close', 'group-toggle', 'light-toggle', 'set-light', 'select-scene', 'start-animation', 'stop-animation'],
  components: {Animate, ToggleSwitch, MenuPanel, Light, Scene, Controls},
  props: {
    lights: {
      type: Object,
    },

    group: {
      type: Object,
    },

    scenes: {
      type: Object,
    },

    title: {
      type: String,
      default: 'Lights',
    },

    animations: {
      type: Object,
      default: () => {},
    },

    colorConverter: {
      type: Object,
      default: () => new ColorConverter(),
    },

    withBackButton: {
      type: Boolean,
      default: true,
    },
  },

  data() {
    return {
      selectedLight: null,
      selectedScene: null,
      selectedView: 'lights',
    }
  },

  computed: {
    anyLightsOn() {
      if (this.group?.state?.any_on != null)
        return this.group.state.any_on

      return Object.values(this.lights).some(light => light.state.on)
    },

    lightsSorted() {
      if (!this.lights)
        return []

      return Object.entries(this.lights)
          .sort((a, b) => a[1].name.localeCompare(b[1].name))
          .map(([id, light]) => {
            return {
              ...light,
              id: id,
            }
          })
    },

    scenesSorted() {
      if (!this.scenes)
        return []

      return Object.entries(this.scenes)
          .sort((a, b) => a[1].name.localeCompare(b[1].name))
          .map(([id, scene]) => {
            return {
              ...scene,
              id: id,
            }
          })
    },

    groupName() {
      if (this.group?.name)
        return this.group.name
      if (this.group?.id != null)
        return `[Group ${this.group.id}]`
      return this.title
    },
  },

  methods: {
    close(event) {
      event.stopPropagation()
      this.$emit('close')
    },

    onSceneSelected(sceneId) {
      this.selectedScene = sceneId
      this.$emit('select-scene', sceneId)
    },
  },
}
</script>

<style lang="scss" scoped>
@import "./groups.scss";
</style>

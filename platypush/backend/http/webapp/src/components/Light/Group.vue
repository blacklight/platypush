<template>
  <div class="light-group-container">
    <MenuPanel>
      <div class="panel-row header">
        <div class="col-3" v-if="group">
          <button class="back-btn" title="Back" @click="close">
            <i class="fas fa-chevron-left" />
          </button>
        </div>

        <div class="col-6 name" :class="{selected: selectedView === 'group'}"
             v-text="groupName" @click="selectedView = selectedView === 'group' ? null : 'group'" />

        <div class="col-3 pull-right" v-if="group">
          <ToggleSwitch :value="group.state.any_on" @input="$emit('group-toggle', group)" />
        </div>
      </div>

      <div class="no-lights" v-if="!lights || !Object.keys(lights).length">
        No lights found
      </div>

      <div class="lights-view" v-else>
        <div class="row view-selector">
          <button :class="{selected: selectedView === 'lights'}" title="Lights" @click="selectedView = 'lights'">
            <i class="icon fas fa-lightbulb" />
            <span class="view-title">&nbsp; Lights</span>
          </button>
          <button :class="{selected: selectedView === 'scenes'}" title="Scenes" @click="selectedView = 'scenes'">
            <i class="icon far fa-image" />
            <span class="view-title">&nbsp; Scenes</span>
          </button>
          <button :class="{selected: selectedView === 'animate'}" title="Animate"
                  @click="selectedView = 'animate'">
            <i class="icon fas fa-video" />
            <span class="view-title">&nbsp; Animate</span>
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

    animations: {
      type: Object,
      default: () => {},
    },

    colorConverter: {
      type: Object,
      default: () => new ColorConverter(),
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
      return 'Lights'
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

<style lang="scss">
.light-group-container {
  width: 100%;
  min-height: 100%;

  .row.panel-row {
    flex-direction: column;

    &.expanded,
    &.selected {
      background: $selected-bg;
    }
  }

  .header {
    padding: 0.5em !important;
    display: flex;
    align-items: center;

    .back-btn {
      border: 0;
      background: none;

      &:hover {
        border: 0;
        color: $default-hover-fg;
      }
    }

    .name {
      text-align: center;

      &.selected {
        color: $selected-fg;
      }

      &:hover {
        color: $default-hover-fg;
      }
    }
  }

  .view-selector {
    width: 100%;
    border-radius: 0;

    button {
      width: 33.3%;
      padding: 1.5em;
      text-align: left;
      opacity: 0.8;
      box-shadow: $plugin-panel-entry-shadow;
      border-right: 0;

      &.selected {
        background: $selected-bg;
      }

      &:hover {
        background: $hover-bg;
      }
    }

    @media screen and (max-width: $tablet) {
      .view-title {
        display: none;
      }

      .icon {
        width: 100%;
        text-align: center;
        font-size: 1.2em;
      }
    }
  }
}
</style>

<style lang="scss">
.light-group-container {
  .group-controls {
    margin: 0;
    padding: 1em;
    background-color: $default-bg-6;
    border-radius: 0 0 1em 1em;

    .controls {
      margin: 0;
      padding: 1em;
    }
  }
}
</style>

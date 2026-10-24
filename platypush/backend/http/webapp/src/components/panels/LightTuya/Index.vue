<template>
  <Loading v-if="loading" />
  <LightPlugin plugin-name="light.tuya" :config="config" :lights="lights" :groups="groups" :scenes="scenes"
               :animations="animations" :initial-group="initialGroup" :loading-groups="loadingGroups"
               :color-converter="colorConverter" @group-toggle="toggleGroup" @light-changed="onLightChanged"
               @light-toggle="toggleLight" @set-light="setLight" @set-group="setGroup"
               @refresh="refresh(true)"/>
</template>

<script>
import LightPlugin from "@/components/panels/Light/Index";
import LightUtils from "@/components/panels/Light/Utils";
import { ColorConverter } from "@/components/panels/Light/color"
import Utils from "@/Utils";
import Loading from "@/components/Loading";

export default {
  name: "LightTuya",
  components: {Loading, LightPlugin},
  mixins: [Utils, LightUtils],
  props: {
    config: {
      type: Object,
      default: () => {},
    },
  },

  data() {
    return {
      loading: false,
      colorConverter: new ColorConverter({
        hue: [0, 360],
        sat: [0, 100],
        bri: [0, 255],
        ct: [153, 500],
      })
    }
  },

  computed: {
    initialGroup() {
      if (!this.config.groups || !Object.keys(this.config.groups).length)
        return null

      const group = this.config.groups instanceof Object
        ? Object.keys(this.config.groups)[0]
        : this.config.groups[0]

      if (group in this.groups)
        return this.groups[group].id
      else if (group in this.groupsByName)
        return this.groupsByName[group].id
      return null
    },
  },

  methods: {
    async getLights() {
      return await this.request('light.tuya.get_lights')
    },

    async getGroups() {
      return await this.request('light.tuya.get_groups')
    },

    async toggleGroup(group) {
      let groups = Object.values(this.groups)
      let args = {
        groups: groups.map((group) => group.name)
      }

      if (group != null) {
        groups = [group]
        args = {
          groups: [group.name],
        }
      }

      await this.groupAction('light.tuya.toggle', args, ...groups)
      await this.refresh(true)
    },

    async toggleLight(light) {
      const lights = [light]
      const args = light != null ? {
        lights: [light.name],
      } : {}

      await this.lightAction('light.tuya.toggle', args, ...lights)
      await this.refresh(true)
    },

    _lightArgs(event) {
      const args = {}
      const value = event.value

      if (value.brightness != null)
        args.brightness = value.brightness
      if (value.temperature != null)
        args.temperature = value.temperature
      if (value.xy != null)
        args.xy = value.xy
      if (value.rgb != null)
        args.rgb = value.rgb
      if (value.hsl != null) {
        args.hue = value.hsl[0]
        args.saturation = value.hsl[1]
      }

      return args
    },

    async setLight(event) {
      const lights = event.light ? [event.light] : Object.keys(this.lights)
      const args = this._lightArgs(event)

      if (event.light)
        args.lights = [event.light.name]

      await this.lightAction('light.tuya.set_lights', args, ...lights)
      await this.refresh(true)
    },

    async setGroup(event) {
      if (!event.groupId)
        return this.setLight(event)

      const group = this.groups[event.groupId]
      const args = {
        groups: [group.name],
        ...this._lightArgs(event),
      }

      await this.groupAction('light.tuya.set_lights', args, group)
      await this.refresh(true)
    },

    async refresh(background) {
      if (!background)
        this.loading = true

      try {
        [this.lights, this.groups] = await Promise.all([
          this.getLights(),
          this.getGroups(),
        ])
      } finally {
        if (!background)
          this.loading = false
      }
    },

    onLightChanged(event) {
      this.lights[event.id].state = {
        ...this.lights[event.id].state,
        ...event.state,
      }
    },
  },

  mounted() {
    this.refresh()
  },
}
</script>

<style lang="scss" scoped>
.lights-plugin {
  @include until($tablet) {
    padding: 0.5em;
  }
}
</style>

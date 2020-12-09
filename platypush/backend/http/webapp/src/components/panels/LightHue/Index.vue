<template>
  <Loading v-if="loading" />
  <LightPlugin plugin-name="light.hue" :config="config" :lights="lights" :groups="groups" :scenes="scenes"
               :animations="animations" :initial-group="initialGroup" :loading-groups="loadingGroups"
               :color-converter="colorConverter" @group-toggle="toggleGroup"
               @light-toggle="toggleLight" @set-light="setLight" @set-group="setGroup" @select-scene="setScene" />
</template>

<script>
import LightPlugin from "@/components/panels/Light/Index";
import LightUtils from "@/components/panels/Light/Utils";
import { ColorConverter } from "@/components/panels/Light/color"
import Utils from "@/Utils";
import Loading from "@/components/Loading";

export default {
  name: "LightHue",
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
        hue: [0, 65535],
        sat: [0, 255],
        bri: [0, 255],
        ct: [150, 500],
      })
    }
  },

  computed: {
    initialGroup() {
      if (!this.config.groups || !Object.keys(this.config.groups).length)
        return null

      const group = this.config.groups[0]
      if (group in this.groups)
        return this.groups[group].id
      else if (group in this.groupsByName)
        return this.groupsByName[group].id
      return null
    },
  },

  methods: {
    async getLights() {
      return await this.request('light.hue.get_lights')
    },

    async getGroups() {
      return Object.entries(await this.request('light.hue.get_groups'))
          .filter((group) => !group[1].recycle && group[1].type.toLowerCase() === 'room')
          .reduce((obj, [id, group]) => {
            obj[id] = group
            return obj
          }, {})
    },

    async getScenes() {
      // return await this.request('light.hue.get_scenes')
      return Object.entries(await this.request('light.hue.get_scenes'))
          .filter((scene) => !scene[1].recycle && scene[1].type.toLowerCase() === 'lightscene')
          .reduce((obj, [id, scene]) => {
            obj[id] = scene
            return obj
          }, {})
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

      await this.groupAction('light.hue.toggle',  args, ...groups)
      await this.refresh(true)
    },

    async toggleLight(light) {
      const lights = [light]
      const args = light != null ? {
        lights: [light.name],
      } : {}

      await this.lightAction('light.hue.toggle',  args, ...lights)
      await this.refresh(true)
    },

    async setLight(event) {
      let lights = Object.keys(this.lights)
      const light = event.light
      const args = {}

      if (light) {
        args.lights = [light.name]
        lights = [light]
      }

      const self = this
      const requests = Object.entries(event.value).map(([attr, value]) => {
        let method = null;
        args.value = value

        switch (attr) {
          case 'brightness':
            method = 'light.hue.bri'
            break

          case 'temperature':
            method = 'light.hue.ct'
            break

          case 'xy':
            method = 'light.hue.xy'
            break
        }

        if (method)
          return self.lightAction(method, args, ...lights)
      }).filter((req) => req != null)

      await Promise.all(requests)
      await this.refresh(true)
    },

    async setGroup(event) {
      if (!event.groupId)
        return this.setLight(event)

      const group = this.groups[event.groupId]
      const args = {
        groups: [group.name],
      }

      const self = this
      const requests = Object.entries(event.value).map(([attr, value]) => {
        let method = null;
        args.value = value

        switch (attr) {
          case 'brightness':
            method = 'light.hue.bri'
            break

          case 'temperature':
            method = 'light.hue.ct'
            break

          case 'xy':
            method = 'light.hue.xy'
            break
        }

        if (method)
          return self.lightAction(method, args, group)
      }).filter((req) => req != null)

      await Promise.all(requests)
      await this.refresh(true)
    },

    async setScene(event) {
      await this.groupAction('light.hue.scene',  {
        name: this.scenes[event.sceneId].name,
        groups: [this.groups[event.groupId].name],
      }, this.groups[event.groupId])

      await this.refresh(true)
    },

    async refresh(background) {
      if (!background)
        this.loading = true

      try {
        [this.lights, this.groups, this.scenes] = await Promise.all([
          this.getLights(),
          this.getGroups(),
          this.getScenes(),
        ])
      } finally {
        if (!background)
          this.loading = false
      }
    },
  },

  mounted() {
    this.refresh()
  },
}
</script>

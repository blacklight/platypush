<template>
  <Loading v-if="loading" />
  <LightPlugin plugin-name="light.hue" :config="config" :lights="lights" :groups="groups" :scenes="scenes"
               :animations="animations" :initial-group="initialGroup" :loading-groups="loadingGroups"
               @group-toggle="toggleGroup" />
</template>

<script>
import LightPlugin from "@/components/panels/Light/Index";
import Utils from "@/Utils";
import Loading from "@/components/Loading";

export default {
  name: "LightHue",
  components: {Loading, LightPlugin},
  mixins: [Utils],
  props: {
    config: {
      type: Object,
      default: () => {},
    },
  },

  data() {
    return {
      lights: {},
      groups: {},
      scenes: {},
      animations: {},
      loading: false,
      loadingLights: {},
      loadingGroups: {},
    }
  },

  computed: {
    groupsByName() {
      if (!this.groups)
        return {}

      return Object.entries(this.groups).reduce((groups, [id, group]) => {
        groups[group.name || id] = {
          ...group,
          id: id,
        }

        return groups
      }, {})
    },

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
      return await this.request('light.hue.get_scenes')
    },

    async toggleGroup(group) {
      const groups = []
      if (group != null)
        groups.push(group.name)

      this.setGroupsLoading(group)
      try {
        await this.request('light.hue.toggle', {
          groups: groups,
        })

        await this.refresh()
      } finally {
        this.unsetGroupsLoading(group)
      }
    },

    async refresh() {
      this.loading = true
      try {
        [this.lights, this.groups, this.scenes] = await Promise.all([
          this.getLights(),
          this.getGroups(),
          this.getScenes(),
        ])
      } finally {
        this.loading = false
      }
    },

    setGroupsLoading(...groups) {
      let loadingGroups = {}
      if (groups.length && groups[0]) {
        for (const group of groups)
          loadingGroups[group.id] = true
      } else {
        loadingGroups = Object.keys(this.groups)
      }

      this.loadingGroups = {...this.loadingGroups, ...loadingGroups}
    },

    unsetGroupsLoading(...groups) {
      for (const group of groups) {
        if (group.id in this.loadingGroups)
          delete this.loadingGroups[group.id]
      }
    },
  },

  mounted() {
    this.refresh()
  },
}
</script>

<script>
export default {
  name: "Utils",
  data() {
    return {
      lights: {},
      groups: {},
      scenes: {},
      animations: {},
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
  },

  methods: {
    _getGroups(groupIds) {
      const groups = groupIds.filter((id) => id != null)
      if (!groups.length)
        return Object.values(this.groups)

      const self = this
      return groups.map((id) => id instanceof Object ? id : self.groups[id])
    },

    _getLights(lightIds) {
      const lights = lightIds.filter((id) => id != null)
      if (!lights.length)
        return Object.values(this.lights)

      const self = this
      return lights.map((id) => id instanceof Object ? id : self.lights[id])
    },

    setGroupsLoading(groupsIds) {
      const self = this
      this._getGroups(groupsIds).forEach((group) => {
        self.loadingGroups[group.id] = true
        if (group.lights)
          self.setLightsLoading(group.lights)
      })
    },

    unsetGroupsLoading(groupsIds) {
      const self = this
      this._getGroups(groupsIds).forEach((group) => {
        if (group.id in self.loadingGroups)
          delete self.loadingGroups[group.id]
        if (group.lights)
          self.setLightsLoading(group.lights)
      })
    },

    setLightsLoading(lightIds) {
      const self = this
      this._getLights(lightIds).forEach((light) => {
        self.loadingLights[light.id] = true
      })
    },

    unsetLightsLoading(lightIds) {
      const self = this
      this._getLights(lightIds).forEach((light) => {
        if (light.id in self.loadingLights)
          delete self.loadingLights[light.id]
      })
    },

    async groupAction(action, args, ...groups) {
      this.setGroupsLoading(groups)
      try {
        return await this.request(action, args)
      } finally {
        this.unsetGroupsLoading(groups)
      }
    },

    async lightAction(action, args, ...lights) {
      this.setLightsLoading(lights)
      try {
        return await this.request(action, args)
      } finally {
        this.unsetLightsLoading(lights)
      }
    },

  },
}
</script>

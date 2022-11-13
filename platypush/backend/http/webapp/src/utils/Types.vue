<script>
export default {
  name: "Types",
  methods: {
    parseBoolean(value) {
      if (typeof value === 'string') {
        value = value.toLowerCase()
        if (value === 'true')
          return true
        if (value === 'false')
          return false

        return !!parseInt(value)
      }

      return !!value
    },

    convertSize(value) {
      if (typeof value === 'string')
        value = parseInt(value)

      let unit = null
      const units = ['B', 'KB', 'MB', 'GB', 'TB']

      units.forEach((u, i) => {
        if (value <= 1024 && unit == null) {
          unit = u
        } else if (value > 1024) {
          if (i === units.length-1) {
            unit = u
          } else {
            value = value/1024
          }
        }
      })

      return `${value.toFixed(2)} ${unit}`
    },

    objectsEqual(a, b) {
      if (typeof(a) !== 'object' || typeof(b) !== 'object')
        return false

      for (const p of Object.keys(a || {})) {
        switch(typeof(a[p])) {
          case 'object':
            if (!this.objectsEqual(a[p], b[p]))
              return false
            break

          case 'function':
            if (a[p].toString() != b[p]?.toString())
              return false
            break

          default:
            if (a[p] != b[p])
              return false
            break
        }
      }

      for (const p of Object.keys(b || {}))
        if (a[p] == null && b[p] != null)
          return false

      return true
    },
  },
}
</script>

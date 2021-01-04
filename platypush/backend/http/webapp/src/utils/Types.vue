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
    }
  },
}
</script>

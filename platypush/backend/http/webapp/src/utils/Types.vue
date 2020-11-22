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
  },
}
</script>

<script>
export default {
  name: "Url",
  methods: {
    parseUrlFragment() {
      return window.location.href.replace(/.*#(\w+)[?;]?.*/, '$1')
    },

    getUrlArgs() {
      return window.location.href
        .replace(/.*#/, '')
        .replace(/.*\?/, '')
        .split(/[&;]/)
        .reduce((acc, obj) => {
          const tokens = obj.split('=')
          acc[tokens[0]] = tokens[1]
          return acc
        }, {})
    },

    setUrlArgs(args) {
      window.location.href = (
        `/#${this.parseUrlFragment()}?${this.fragmentFromArgs(args)}`
      )
    },

    fragmentFromArgs(args) {
      return Object.entries(args)
        .map(
          ([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`
        )
        .join('&')
    },
  },
}
</script>


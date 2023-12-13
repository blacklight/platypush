<script>
export default {
  name: "Url",
  methods: {
    parseUrlFragment() {
      return window.location.hash.replace(/^#/, '').replace(/\?.*/, '')
    },

    getUrlArgs() {
      const argsString = window.location.hash.split('?').slice(1)
      if (!argsString.length)
        return {}

      return argsString[0]
        .split(/[&;]/)
        .reduce((acc, obj) => {
          const tokens = obj.split('=')
          if (tokens[0]?.length)
            acc[tokens[0]] = tokens[1]
          return acc
        }, {})
    },

    setUrlArgs(args) {
      args = {...this.getUrlArgs(), ...args}
      window.location.href = (
        `${window.location.pathname}#${this.parseUrlFragment()}?${this.fragmentFromArgs(args)}`
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


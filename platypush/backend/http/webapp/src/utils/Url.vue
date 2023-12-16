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
      const curArgs = this.getUrlArgs()
      args = Object.entries(args)
        .reduce((acc, [key, value]) => {
          if (value != null)
            acc[key] = value
          else if (curArgs[key] != null)
            delete curArgs[key]
          return acc
        }, {})

      args = {...curArgs, ...args}
      let location = `${window.location.pathname}#${this.parseUrlFragment()}`
      if (Object.keys(args).length)
        location += `?${this.fragmentFromArgs(args)}`

      window.location.href = location
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


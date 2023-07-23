<script>
export default {
  name: "Cookies",
  methods: {
    getCookies() {
      return document.cookie.split(/;\s*/).reduce((obj, item) => {
        const [k, v] = item.split('=')
        obj[k] = v
        return obj
      }, {})
    },

    getCookie(name) {
      return this.getCookies()[name]
    },

    setCookie(name, value, opts) {
      document.cookie = (
        `${name}=${value}; path=${opts?.path || '/'}` + (
          opts?.expires ? `; expires=${opts?.expires.toISOString()}` : ''
        )
      )
    },

    deleteCookie(name) {
      document.cookie = (
        `${name}=; expires=1970-01-01T00:00:00Z`
      )
    },
  }
}
</script>

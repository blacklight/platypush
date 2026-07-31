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
      const isSecure = window?.location?.protocol === 'https:'
      const parts = [
        `${name}=${value}`,
        `path=${opts?.path || '/'}`,
      ]

      if (opts?.expires) {
        parts.push(`expires=${new Date(opts.expires).toUTCString()}`)
      }

      if (isSecure) {
        parts.push('Secure')
      }

      parts.push(`SameSite=${opts?.sameSite || 'Lax'}`)
      document.cookie = parts.join('; ')
    },

    deleteCookie(name) {
      const isSecure = window?.location?.protocol === 'https:'
      const parts = [
        `${name}=`,
        'expires=1970-01-01T00:00:00Z',
        'path=/',
      ]

      if (isSecure) {
        parts.push('Secure')
      }

      parts.push('SameSite=Lax')
      document.cookie = parts.join('; ')
    },
  }
}
</script>

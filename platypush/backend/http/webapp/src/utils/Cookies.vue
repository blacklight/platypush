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
    }
  }
}
</script>

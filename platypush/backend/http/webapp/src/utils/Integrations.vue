<script>
export default {
  name: "Integrations",
  methods: {
    pluginDisplayName(name) {
      const words = name.split('.')
      words.forEach((word, idx) => {
        words[idx] = word.charAt(0).toUpperCase() + word.slice(1)
      })

      if (words.length > 1)
        words[0] = `[${words[0]}]`

      return words.join(' ')
    },
  }
}
</script>

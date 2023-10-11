<script>
export default {
  name: "Text",
  methods: {
    capitalize(text) {
      if (!text?.length)
        return text

      return text.charAt(0).toUpperCase() + text.slice(1)
    },

    prettify(text) {
      return text.split('_').map((t) => this.capitalize(t)).join(' ')
    },

    indent(text, tabs = 1) {
      return text.split('\n').map((t) => `${'\t'.repeat(tabs)}${t}`).join('\n')
    },
  },
}
</script>

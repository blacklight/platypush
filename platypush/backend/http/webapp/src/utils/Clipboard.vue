<script>
export default {
  name: "Clipboard",
  methods: {
    async copyToClipboard(text) {
      await navigator.clipboard.writeText(text)
      this.notify({
        text: 'Copied to the clipboard',
        image: {
          icon: 'clipboard',
        },
      })
    },
  },
}
</script>


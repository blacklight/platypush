<script>
export default {
  name: "Panel",
  emits: ['mounted'],
  props: {
    // Plugin configuration.
    config: {
      type: Object,
      default: () => {},
    },

    // Plugin name.
    pluginName: {
      type: String,
      required: true,
    },
  },

  data() {
    return {
      loading: false,
    }
  },

  mounted() {
    this.$emit('mounted', this)
  }
}
</script>

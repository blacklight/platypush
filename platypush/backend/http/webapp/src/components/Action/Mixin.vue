<script>
export default {
  methods: {
    getCondition(value) {
      value = this.getKey(value) || value
      return value?.trim?.()?.match(/^if\s*\$\{(.*)\}\s*$/i)?.[1]?.trim?.()
    },

    getKey(value) {
      return this.isKeyword(value) ? Object.keys(value)[0] : null
    },

    isAction(value) {
      return typeof value === 'object' && !Array.isArray(value) && (value.action || value.name)
    },

    isActionsBlock(value) {
      return this.getCondition(value) || this.isElse(value)
    },

    isKeyword(value) {
      return (
        value &&
        typeof value === 'object' &&
        !Array.isArray(value) &&
        Object.keys(value).length === 1 &&
        !this.isAction(value)
      )
    },

    isElse(value) {
      return (this.getKey(value) || value)?.toLowerCase?.()?.trim?.() === 'else'
    },
  },
}
</script>

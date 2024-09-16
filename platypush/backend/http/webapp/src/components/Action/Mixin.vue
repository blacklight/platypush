<script>
export default {
  methods: {
    getCondition(value) {
      value = this.getKey(value) || value
      return value?.trim?.()?.match(/^if\s*\$\{(.*)\}\s*$/i)?.[1]?.trim?.()
    },

    getFor(value) {
      value = this.getKey(value) || value
      let m = value?.trim?.()?.match(/^for(k?)\s*(.*)\s*in\s*\$\{(.*)\}\s*$/i)
      if (!m)
        return null

      return {
        async: m[1].length > 0,
        iterator: m[2].trim(),
        iterable: m[3].trim(),
      }
    },

    getKey(value) {
      return this.isKeyword(value) ? Object.keys(value)[0] : null
    },

    getWhile(value) {
      value = this.getKey(value) || value
      return value?.trim?.()?.match(/^while\s*\$\{(.*)\}\s*$/i)?.[1]?.trim?.()
    },

    isAction(value) {
      return typeof value === 'object' && !Array.isArray(value) && (value.action || value.name)
    },

    isActionsBlock(value) {
      return this.getCondition(value) || this.isElse(value) || this.getFor(value) || this.getWhile(value)
    },

    isBreak(value) {
      return value?.toLowerCase?.()?.trim?.() === 'break'
    },

    isContinue(value) {
      return value?.toLowerCase?.()?.trim?.() === 'continue'
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

    isReturn(value) {
      if (!value)
        return false

      if (Array.isArray(value))
        return value.length === 1 && value[0]?.length && value[0].match(/^return\s*$/i)

      return this.getKey(value) === 'return'
    },

    isSet(value) {
      return this.getKey(value) === 'set'
    },
  },
}
</script>

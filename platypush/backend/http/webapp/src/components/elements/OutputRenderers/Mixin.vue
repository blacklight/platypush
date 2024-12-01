<script>
import 'highlight.js/lib/common'
import 'highlight.js/styles/night-owl.min.css'
import hljs from "highlight.js"

import Utils from '@/Utils'

export default {
  mixins: [Utils],
  props: {
    output: {
      type: [Object, String],
      required: true,
    },

    filter: {
      type: String,
      default: '',
    },

    index: {
      type: Number,
      default: 0,
    },
  },

  data() {
    return {
      expanded: false,
    }
  },

  computed: {
    highlightedText() {
      return hljs.highlight(
        this.outputString,
        {language: this.isJson ? 'json' : 'plaintext'}
      ).value
    },

    isJson() {
      if (typeof this.output === 'object') {
        return true
      }

      try {
        JSON.parse(this.output)
        return true
      } catch (err) {
        return false
      }
    },

    outputString() {
      if (!Object.keys(this.output || {})?.length) {
        return ''
      }

      try {
        return JSON.stringify(this.output, null, this.expanded ? 2 : 0)
      } catch (err) {
        return this.output
      }
    },
  },
}
</script>

<script>
import Utils from "@/Utils"

export default {
  name: "EntityMixin",
  mixins: [Utils],
  emits: ['input'],
  props: {
    loading: {
      type: Boolean,
      default: false,
    },

    error: {
      type: Boolean,
      default: false,
    },

    value: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      modalVisible: false,
    }
  },

  computed: {
    type() {
      let entityType = (this.value.type || '')
      return entityType.charAt(0).toUpperCase() + entityType.slice(1)
    },
  },
}
</script>

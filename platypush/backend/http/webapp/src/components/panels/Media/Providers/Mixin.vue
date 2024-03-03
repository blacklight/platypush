<script>
import Utils from "@/Utils";

export default {
  emits: ['back', 'path-change', 'play'],
  mixins: [Utils],
  props: {
    filter: {
      type: String,
      default: '',
    },
  },

  data() {
    return {
      loading: false,
    }
  },
}
</script>

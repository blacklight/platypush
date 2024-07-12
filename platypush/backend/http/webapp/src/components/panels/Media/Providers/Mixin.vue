<script>
import Utils from "@/Utils";

export default {
  mixins: [Utils],
  emits: [
    'add-to-playlist',
    'back',
    'create-playlist',
    'path-change',
    'play',
    'remove-from-playlist',
    'remove-playlist',
    'rename-playlist',
  ],

  props: {
    filter: {
      type: String,
      default: '',
    },

    selectedPlaylist: {
      default: null,
    },
  },

  data() {
    return {
      loading: false,
    }
  },
}
</script>

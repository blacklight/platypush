<script>
import Utils from "@/Utils";

export default {
  mixins: [Utils],
  emits: [
    'add-to-playlist',
    'back',
    'create-playlist',
    'download',
    'download-audio',
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

    loading: {
      type: Boolean,
      default: false,
    },

    mediaPlugin: {
      type: String,
    },

    selectedPlaylist: {
      default: null,
    },

    selectedChannel: {
      default: null,
    },
  },

  data() {
    return {
      loading_: false,
    }
  },

  computed: {
    isLoading() {
      return this.loading || this.loading_
    },
  },
}
</script>

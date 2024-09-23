<script>
export default {
  props: {
    items: {
      type: Array,
      required: true,
    },

    value: {
      type: [String, Number, Object, Array, Boolean],
      default: "",
    },

    disabled: {
      type: Boolean,
      default: false,
    },

    autofocus: {
      type: Boolean,
      default: false,
    },

    label: {
      type: String,
    },

    placeholder: {
      type: String,
    },

    inputOnBlur: {
      type: Boolean,
      default: true,
    },

    inputOnSelect: {
      type: Boolean,
      default: true,
    },

    selectOnTab: {
      type: Boolean,
      default: true,
    },

    showAllItems: {
      type: Boolean,
      default: false,
    },

    showResultsWhenBlank: {
      type: Boolean,
      default: false,
    },
  },
}
</script>

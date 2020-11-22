<script>
export default {
  name: "DateTime",
  methods: {
    formatDate(date) {
      return date.toDateString().substring(0, 10)
    },

    formatTime(date, seconds=true) {
      return date.toTimeString().substring(0, seconds ? 8 : 5)
    },
  },
}
</script>

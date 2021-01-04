<script>
export default {
  name: "DateTime",
  methods: {
    formatDate(date, year=false) {
      if (typeof date === 'string')
        date = new Date(Date.parse(date))

      return date.toDateString().substring(0, year ? 14 : 10)
    },

    formatTime(date, seconds=true) {
      if (typeof date === 'string')
        date = new Date(Date.parse(date))

      return date.toTimeString().substring(0, seconds ? 8 : 5)
    },
  },
}
</script>

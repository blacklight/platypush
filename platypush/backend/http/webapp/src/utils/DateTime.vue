<script>
export default {
  name: "DateTime",
  methods: {
    formatDate(date, year=false) {
      if (typeof date === 'string')
        date = new Date(Date.parse(date))

      return date.toDateString().substring(0, year ? 15 : 10)
    },

    formatTime(date, seconds=true) {
      if (typeof date === 'string')
        date = new Date(Date.parse(date))

      return date.toTimeString().substring(0, seconds ? 8 : 5)
    },

    formatDateTime(date, year=false, seconds=true) {
      if (typeof date === 'string')
        date = new Date(Date.parse(date))

      return `${this.formatDate(date, year)}, ${this.formatTime(date, seconds)}`
    },
  },
}
</script>

<script>
export default {
  name: "DateTime",
  methods: {
    formatDate(date, year=false) {
      if (typeof date === 'number')
        date = new Date(date * 1000)
      else if (typeof date === 'string')
        date = new Date(Date.parse(date))

      return date.toDateString().substring(0, year ? 15 : 10)
    },

    formatTime(date, seconds=true) {
      if (typeof date === 'number')
        date = new Date(date * 1000)
      if (typeof date === 'string')
        date = new Date(Date.parse(date))

      return date.toTimeString().substring(0, seconds ? 8 : 5)
    },

    formatDateTime(date, year=false, seconds=true, skipTimeIfMidnight=false) {
      const now = new Date()

      if (typeof date === 'number')
        date = new Date(date * 1000)
      if (typeof date === 'string')
        date = new Date(Date.parse(date))
      if (now.getFullYear() !== date.getFullYear())
        year = true

      if (skipTimeIfMidnight && date.getHours() === 0 && date.getMinutes() === 0 && date.getSeconds() === 0)
        return this.formatDate(date, year)

      return `${this.formatDate(date, year)}, ${this.formatTime(date, seconds)}`
    },

    formatDuration(duration, seconds=true) {
      if (duration == null)
        return ''

      let hours = Math.floor(duration / 3600)
      let minutes = Math.floor((duration % 3600) / 60)
      let secs = duration % 60

      if (hours > 0)
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
      else if (minutes > 0)
        return `${minutes}:${secs.toString().padStart(2, '0')}`
      else
        return seconds ? `0:${secs.toString().padStart(2, '0')}` : `0:00`
    },
  },
}
</script>

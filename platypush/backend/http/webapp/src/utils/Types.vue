<script>
export default {
  name: "Types",
  methods: {
    parseBoolean(value) {
      if (typeof value === 'string') {
        value = value.toLowerCase()
        if (value === 'true')
          return true
        if (value === 'false')
          return false

        return !!parseInt(value)
      }

      return !!value
    },

    convertSize(value) {
      if (typeof value === 'string')
        value = parseInt(value)

      let unit = null
      const units = ['B', 'KB', 'MB', 'GB', 'TB']

      units.forEach((u, i) => {
        if (value <= 1024 && unit == null) {
          unit = u
        } else if (value > 1024) {
          if (i === units.length-1) {
            unit = u
          } else {
            value = value/1024
          }
        }
      })

      return `${value.toFixed(2)} ${unit}`
    },

    convertTime(time) {
      const t = {}
      const ret = []

      time = parseFloat(time);   // Normalize strings
      t.d = Math.round(time/86400)
      t.h = Math.round(time/3600 - t.d*24)
      t.m = Math.round(time/60 - (t.d*24 + t.h*60))
      t.s = Math.round(time - (t.d*24 + t.h*3600 + t.m*60), 1)

      if (parseInt(t.d)) {
        let d = t.d + ' day'
        if (t.d > 1) {
          d += 's'
        }
        ret.push(d)
      }

      if (parseInt(t.h)) {
        let h = t.h + ' hour'
        if (t.h > 1) {
          h += 's'
        }
        ret.push(h)
      }

      if (parseInt(t.m)) {
        let m = t.m + ' minute'
        if (t.m > 1) {
          m += 's'
        }
        ret.push(m)
      }

      let s = t.s + ' second'
      if (t.s > 1) {
        s += 's'
      }
      ret.push(s)

      return ret.join(' ')
    },

    objectsEqual(a, b) {
      if (typeof(a) !== 'object' || typeof(b) !== 'object')
        return false

      if (a == null || b == null) {
        return a == null && b == null
      }

      for (const p of Object.keys(a || {})) {
        switch(typeof(a[p])) {
          case 'object':
            if (!this.objectsEqual(a[p], b[p]))
              return false
            break

          case 'function':
            if (a[p].toString() != b[p]?.toString())
              return false
            break

          default:
            if (a[p] != b[p])
              return false
            break
        }
      }

      for (const p of Object.keys(b || {}))
        if (a[p] == null && b[p] != null)
          return false

      return true
    },

    round(value, decimals) {
      return Number(Math.round(value+'e'+decimals)+'e-'+decimals);
    },
  },
}
</script>

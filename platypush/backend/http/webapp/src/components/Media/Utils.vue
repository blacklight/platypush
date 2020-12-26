<script>
export default {
  name: "Utils",
  methods: {
    convertTime(time) {
      time = parseFloat(time);   // Normalize strings
      const t = {}
      t.h = '' + parseInt(time/3600)
      t.m = '' + parseInt(time/60 - t.h*60)
      t.s = '' + parseInt(time - (t.h*3600 + t.m*60))

      for (const attr of ['m','s']) {
        if (parseInt(t[attr]) < 10) {
          t[attr] = '0' + t[attr]
        }
      }

      const ret = []
      if (parseInt(t.h)) {
        ret.push(t.h)
      }

      ret.push(t.m, t.s)
      return ret.join(':')
    },
  },
}
</script>

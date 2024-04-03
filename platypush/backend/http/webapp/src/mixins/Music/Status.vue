<script>
export default {
  methods: {
    parseStatus(status) {
      return Object.entries(status).reduce((obj, [k, v]) => {
        switch (k) {
          case 'bitrate':
          case 'volume':
            obj[k] = parseInt(v)
            break

          case 'consume':
          case 'random':
          case 'repeat':
          case 'single':
            obj[k] = !!parseInt(+v)
            break

          case 'playing_pos':
          case 'song': // Legacy mpd format
            obj.playingPos = parseInt(v)
            break

          case 'time':
            if (v.split) {  // Handle the `elapsed:duration` legacy mpd format
              v = v.split(':')

              if (v.length === 1) {
                obj.elapsed = parseInt(v[0])
              } else {
                obj.elapsed = parseInt(v[0])
                obj.duration = parseInt(v[1])
              }
            } else {
              obj.elapsed = v
            }
            break

          case 'track':
            if (v?.time != null) {
              obj.duration = v.time
            }

            if (v?.playlistPos != null) {
              obj.playingPos = v.pos
            }
            break

          case 'duration':
            obj.duration = parseInt(v)
            break

          case 'elapsed':
            break

          default:
            obj[k] = v
            break
        }

        return obj
      }, {})
    },
  }
}
</script>

<script>
import Utils from "@/Utils";

export default {
  name: "Utils",
  mixins: [Utils],

  computed: {
    audioExtensions() {
      return new Set([
        '3gp', 'aa', 'aac', 'aax', 'act', 'aiff', 'amr', 'ape', 'au',
        'awb', 'dct', 'dss', 'dvf', 'flac', 'gsm', 'iklax', 'ivs',
        'm4a', 'm4b', 'm4p', 'mmf', 'mp3', 'mpc', 'msv', 'nmf', 'nsf',
        'ogg,', 'opus', 'ra,', 'raw', 'sln', 'tta', 'vox', 'wav',
        'wma', 'wv', 'webm', '8svx',
      ])
    },

    videoExtensions() {
      return new Set([
        'webm', 'mkv', 'flv', 'flv', 'vob', 'ogv', 'ogg', 'drc', 'gif',
        'gifv', 'mng', 'avi', 'mts', 'm2ts', 'mov', 'qt', 'wmv', 'yuv',
        'rm', 'rmvb', 'asf', 'amv', 'mp4', 'm4p', 'm4v', 'mpg', 'mp2',
        'mpeg', 'mpe', 'mpv', 'mpg', 'mpeg', 'm2v', 'm4v', 'svi',
        '3gp', '3g2', 'mxf', 'roq', 'nsv', 'flv', 'f4v', 'f4p', 'f4a', 'f4b',
      ])
    },

    mediaExtensions() {
      return new Set([...this.videoExtensions, ...this.audioExtensions])
    },
  },

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

    async startStreaming(resource, pluginName, download=false) {
      let url = resource
      let subtitles = null

      if (resource instanceof Object) {
        url = resource.url
        subtitles = resource.subtitles
      } else {
        resource = {url: url}
      }

      const ret = await this.request(`${pluginName}.start_streaming`, {
        media: url,
        subtitles: subtitles,
        download: download,
      })

      return {...resource, ...ret}
    },

    async stopStreaming(mediaId, pluginName) {
      await this.request(`${pluginName}.stop_streaming`, {media_id: mediaId})
    },
  },
}
</script>

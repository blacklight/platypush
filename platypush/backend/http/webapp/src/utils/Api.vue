<script>
import axios from 'axios'

export default {
  name: "Api",
  methods: {
    execute(request, timeout=60000) {
      const opts = {};

      if (!('target' in request) || !request['target']) {
        request['target'] = 'localhost'
      }

      if (!('type' in request) || !request['type']) {
        request['type'] = 'request'
      }

      // TODO Proper auth/token management
      // if (window.config.token) {
      //   opts.headers = {
      //     'X-Token': window.config.token
      //   }
      // }

      if (timeout) {
        opts.timeout = timeout
      }

      return new Promise((resolve, reject) => {
        axios.post('/execute', request, opts)
            .then((response) => {
              response = response.data.response
              if (!response.errors.length) {
                resolve(response.output);
              } else {
                const error = response.errors[0]
                this.notify({
                  text: error,
                  error: true,
                })

                reject(error)
              }
            })
            .catch((error) => {
              this.notify({
                text: error,
                error: true,
              })

              reject(error)
            })
      })
    },

    request(action, args={}, timeout=60000) {
      return this.execute({
        type: 'request',
        action: action,
        args: args,
      }, timeout);
    }
  },
}
</script>


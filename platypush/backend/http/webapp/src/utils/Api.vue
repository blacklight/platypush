<script>
import axios from 'axios'

export default {
  name: "Api",
  methods: {
    execute(request, timeout=60000, showError=true) {
      const opts = {};

      if (!('target' in request) || !request['target']) {
        request['target'] = 'localhost'
      }

      if (!('type' in request) || !request['type']) {
        request['type'] = 'request'
      }

      if (timeout) {
        opts.timeout = timeout
      }

      return new Promise((resolve, reject) => {
        axios.post('/execute', request, opts)
            .then((response) => {
              response = response.data.response
              if (!response.errors?.length) {
                resolve(response.output);
              } else {
                const error = response.errors?.[0] || response

                if (showError) {
                  this.notify({
                    text: error,
                    error: true,
                  })
                }

                reject(error)
              }
            })
            .catch((error) => {
              // No users present -> redirect to the registration page
              if (
                error?.response?.data?.code === 412 &&
                window.location.pathname !== '/register'
              ) {
                window.location.href = '/register?redirect=' + window.location.href.split('/').slice(3).join('/')
                return
              }

              // Unauthorized -> redirect to the login page
              if (
                error?.response?.data?.code === 401 &&
                window.location.pathname !== '/login'
              ) {
                window.location.href = '/login?redirect=' + window.location.href.split('/').slice(3).join('/')
                return
              }

              console.log(error)
              if (showError)
                this.notify({
                  text: error,
                  error: true,
                })

              reject(error)
            })
      })
    },

    request(action, args={}, timeout=60000, showError=true) {
      return this.execute({
        type: 'request',
        action: action,
        args: args,
      }, timeout, showError);
    },

    timeout(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    },
  },
}
</script>


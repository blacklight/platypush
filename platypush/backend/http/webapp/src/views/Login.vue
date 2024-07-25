<template>
  <Loading v-if="!initialized" />

  <div class="login-container" v-else>
    <form class="login" method="POST" @submit="submitForm" v-if="!isAuthenticated">
      <div class="header">
        <span class="logo">
          <img src="/logo.svg" alt="logo" />
        </span>
        <span class="text">Platypush</span>
      </div>

      <div class="row">
        <label>
          <input :type="requires2fa ? 'hidden' : 'text'"
                 name="username"
                 :disabled="authenticating"
                 placeholder="Username"
                 ref="username">
        </label>
      </div>

      <div class="row">
        <label>
          <input :type="requires2fa ? 'hidden' : 'password'"
                 name="password"
                 :disabled="authenticating"
                 placeholder="Password">
        </label>
      </div>

      <div class="row" v-if="requires2fa">
        <label>
          <input type="text"
                 name="code"
                 :disabled="authenticating"
                 placeholder="2FA code"
                 ref="code">
        </label>
      </div>

      <div class="row" v-if="register">
        <label>
          <input type="password"
                 name="confirm_password"
                 :disabled="authenticating"
                 placeholder="Confirm password">
        </label>
      </div>

      <div class="row buttons">
        <button type="submit"
                class="btn btn-primary"
                :class="{loading: authenticating}"
                :disabled="authenticating">
          <Loading v-if="authenticating" />
          {{ register ? 'Register' : 'Login' }}
        </button>
      </div>

      <div class="row pull-right">
        <label class="checkbox">
          <input type="checkbox" name="remember">&nbsp;
          Keep me logged in on this device &nbsp;
        </label>
      </div>

      <div class="auth-error" v-if="authError">
        {{ authError }}
      </div>
    </form>
  </div>
</template>

<script>
import Loading from "@/components/Loading";
import Utils from "@/Utils";
import axios from 'axios'

export default {
  name: "Login",
  mixins: [Utils],
  components: {
    Loading,
  },

  props: {
    // Set to true for a registration form, false for a login form
    register: {
      type: Boolean,
      required: false,
      default: false,
    },
  },

  computed: {
    redirect() {
      return this.$route.query.redirect?.length ? this.$route.query.redirect : '/'
    },
  },

  data() {
    return {
      authError: null,
      authenticating: false,
      isAuthenticated: false,
      initialized: false,
      requires2fa: false,
    }
  },

  methods: {
    async submitForm(e) {
      e.preventDefault();
      const form = e.target
      const data = new FormData(form)
      const url = `/auth?type=${this.register ? 'register' : 'login'}`

      if (this.register && data.get('password') !== data.get('confirm_password')) {
        this.authError = "Passwords don't match"
        return
      }

      this.authError = null

      try {
        const authStatus = await axios.post(url, data)
        const sessionToken = authStatus?.data?.session_token
        if (sessionToken) {
          const expiresAt = authStatus.expires_at ? Date.parse(authStatus.expires_at) : null
          this.isAuthenticated = true
          this.setCookie('session_token', sessionToken, {
            expires: expiresAt,
          })
          window.location.href = authStatus.redirect || this.redirect
        } else {
          this.authError = "Invalid credentials"
        }
      } catch (e) {
        if (e.response?.data?.error === 'MISSING_OTP_CODE') {
          this.requires2fa = true
          this.$nextTick(() => {
            this.$refs.code?.focus()
          })
        } else {
          this.authError = e.response.data.message || e.response.data.error
          if (e.response?.status === 401) {
            this.authError = this.authError || "Invalid credentials"
          } else {
            this.authError = this.authError || "An error occurred while processing the request"
            if (e.response)
              console.error(e.response.status, e.response.data)
            else
              console.error(e)
          }
        }
      }
    },

    async checkAuth() {
      try {
        const authStatus = await axios.get('/auth')
        if (authStatus.data.session_token) {
          this.isAuthenticated = true
          window.location.href = authStatus.redirect || this.redirect
        }
      } catch (e) {
        this.isAuthenticated = false
      } finally {
        this.initialized = true
      }
    },
  },

  async created() {
    await this.checkAuth()
  },

  async mounted() {
    this.$nextTick(() => {
      this.$refs.username?.focus()
    })
  },
}
</script>

<style lang="scss" scoped>
body {
  width: 100vw;
  height: 100vh;
  margin: 0;
}

.login-container {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $default-bg-6;
}

.header {
  font-size: 1.2em;
  margin-bottom: 2em;
  display: flex;
  justify-content: center;
  align-items: center;

  .logo {
    width: 3em;
    height: 3em;
    display: inline-flex;
    background-size: cover;
  }

  .text {
    font-family: Poppins, sans-serif;
    margin-left: .5em;
  }
}

form {
  display: flex;
  flex-direction: column;
  padding: 4em;
  border: $default-border-3;
  border-radius: 3em;
  box-shadow: 2px 2px 3px 3px $border-color-2;
  background: $background-color;

  .row {
    margin: 0.5em 0;
  }

  input[type=text],
  input[type=password] {
    width: 100%;
  }

  [type=submit],
  input[type=password] {
    border-radius: 1em;
  }

  input[type=password] {
    padding: .25em .5em;
  }

  .checkbox {
    display: flex;
    font-size: 0.8em;
  }

  .buttons {
    text-align: center;

    [type=submit] {
      position: relative;
      width: 6em;
      height: 2.5em;
      padding: .5em .75em;
      display: inline-flex;
      align-items: center;
      justify-content: center;

      &.loading {
        background: none;
        border: none;
        cursor: not-allowed;
      }
    }
  }

  .auth-error {
    background: $error-bg;
    display: flex;
    margin: 1em 0 -2em 0;
    padding: .5em;
    align-items: center;
    justify-content: center;
    border: $notification-error-border;
    border-radius: 1em;
  }
}

a {
  color: $default-link-fg;
}
</style>

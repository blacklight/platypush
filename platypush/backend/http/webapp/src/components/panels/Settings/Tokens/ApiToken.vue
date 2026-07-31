<template>
  <div class="token-container">
    <Loading v-if="loading" />

    <Modal ref="tokenModal">
      <div class="token-container">
        <label>
          This is your generated token. Treat it carefully and do not share it with untrusted parties.<br/>
          Also, make sure to save it - it WILL NOT be displayed again.
        </label>

        <textarea class="token" v-text="token" @focus="copyToClipboard($event.target.value)" />
      </div>
    </Modal>

    <Modal title="Generate an API token"
           ref="tokenParamsModal"
           @open="$nextTick(() => $refs.generateTokenForm.name.focus())"
           @close="$refs.generateTokenForm.reset()">
      <div class="form-container">
        <p>Generate a new API token using your current authenticated session.</p>

        <form @submit.prevent="generateToken" ref="generateTokenForm">
          <label>
            <span>
              A friendly name used to identify this token - such as <code>My
              App</code> or <code>My Site</code>.
            </span>
            <span>
              <input type="text" name="name" placeholder="Token name">
            </span>
          </label>

          <label>
            <span>Token validity in days</span>
            <span>
              <input type="text" name="validityDays" placeholder="Validity in days">
            </span>
          </label>

          <span class="note">
            Decimal values are also supported - e.g. <i>0.5</i> means half a
            day (12 hours). An empty or zero value means that the token has
            no expiry date.
          </span>

          <label>
            <input type="submit" class="btn btn-primary" value="Generate API Token">
          </label>
        </form>
      </div>
    </Modal>

    <Modal title="API Tokens" ref="tokensModal" @close="showTokens = false">
      <TokensList v-if="showTokens" />
    </Modal>

    <div class="body">
      <div class="buttons">
        <label>
          <button class="btn btn-primary" @click="$refs.tokenParamsModal.show()">
            Generate API Token
          </button>
        </label>

        <label>
          <button class="btn btn-default" @click="showTokens = true">
            Manage Tokens
          </button>
        </label>
      </div>

      <p>
        <b>API tokens</b> are randomly generated tokens that are stored
        encrypted on the server, and can be used to authenticate with the
        Platypush API.
      </p>

      <p>
        When compared to the
        <a href="/#settings?page=tokens&type=jwt">JWT tokens</a>, API tokens
        have the following advantages:
      </p>

      <ul>
        <li>They can be revoked at any time by the user who generated
          them, while JWT tokens can only be revoked by changing the
          user's password.</li>
        <li>Their payload is random and not generated from the user's
          password, so even if an attacker gains access to the server's
          encryption keys, they cannot impersonate the user.</li>
        <li>They can be generated with a friendly name that can be used
          to identify the token.</li>
      </ul>

      <Description />
    </div>
  </div>
</template>

<script>
import axios from "axios";
import Description from "./Description";
import Loading from "@/components/Loading";
import Utils from "@/Utils";
import Modal from "@/components/Modal";
import TokensList from "./TokensList";

export default {
  name: "Token",
  mixins: [Utils],
  components: {
    Description,
    Loading,
    Modal,
    TokensList,
  },

  props: {
    currentUser: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      loading: false,
      showTokens: false,
      token: null,
    }
  },

  methods: {
    async getCsrfToken() {
      let csrfToken = this.getCookie('csrf_token')
      if (csrfToken) {
        return csrfToken
      }

      // Fallback: if the csrf_token cookie is not available,
      // fetch it from the current session and set it.
      try {
        const authStatus = await axios.get('/auth')
        const token = authStatus?.data?.csrf_token
        if (token) {
          const expiresAt = authStatus?.data?.expires_at
            ? new Date(authStatus.data.expires_at)
            : null
          this.setCookie('csrf_token', token, {expires: expiresAt})
          return token
        }
      } catch (e) {
        console.error('Failed to refresh CSRF token', e)
      }

      return null
    },

    async generateToken(event) {
      const name = event.target.name.value
      let validityDays = event.target.validityDays?.value?.length ? parseFloat(event.target.validityDays.value) : 0
      if (!validityDays)
        validityDays = null

      const csrfToken = await this.getCsrfToken()
      if (!csrfToken) {
        this.notify({
          text: 'Your session has expired, please log in again.',
          error: true,
        })
        return
      }

      this.loading = true
      try {
        this.token = (await axios.post(
          '/auth?type=token',
          {
            name: name,
            expiry_days: validityDays,
          },
          {
            headers: {
              'X-CSRF-Token': csrfToken,
            },
          },
        )).data.token

        if (this.token?.length)
          this.$refs.tokenModal.show()
      } catch (e) {
        console.error(e.toString())
        const status = e?.response?.status
        const error = e?.response?.data?.error
        let message

        if (status === 401 || error === 'INVALID_SESSION') {
          message = 'Your session has expired, please log in again.'
          this.deleteCookie('session_token')
          this.deleteCookie('csrf_token')
        } else if (status === 403 || error === 'INVALID_CSRF') {
          message = 'Authorization error, please log in again.'
          this.deleteCookie('csrf_token')
        } else if (error === 'TOKEN_NAME_EXISTS') {
          message = e?.response?.data?.message || 'A token with this name already exists.'
        } else {
          message = e?.response?.data?.message || e?.message || e?.toString()
        }

        this.notify({
          text: message,
          error: true,
        })
      } finally {
        this.loading = false
      }
    },
  },

  watch: {
    showTokens(value) {
      if (value) {
        this.$refs.tokensModal.show()
      } else {
        this.$refs.tokensModal.close()
      }
    },
  },
}
</script>

<style lang="scss">
@import "style.scss";

.buttons {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;

  label {
    width: 50%;
    display: flex;
    justify-content: center;
    cursor: pointer;
  }
}
</style>

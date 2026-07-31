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

    <Modal title="Generate a JWT token"
           ref="tokenParamsModal"
           @open="$nextTick(() => $refs.password?.focus())"
           @close="$refs.generateTokenForm.reset()">
      <div class="form-container">
        <p>Confirm your credentials in order to generate a new JWT token.</p>

        <form @submit.prevent="generateToken" ref="generateTokenForm">
          <label>
            <span>Confirm password</span>
            <span>
              <input type="password" name="password" ref="password" placeholder="Password">
            </span>
          </label>

          <label v-if="requires2fa">
            <span>OTP code</span>
            <span>
              <input type="text" name="code" ref="code" placeholder="OTP code">
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
            <input type="submit" class="btn btn-primary" value="Generate JWT Token">
          </label>
        </form>
      </div>
    </Modal>

    <div class="body">
      <label class="generate-btn-container">
        <button class="btn btn-primary" @click="$refs.tokenParamsModal.show()">
          Generate JWT Token
        </button>
      </label>

      <p>
        <b>JWT tokens</b> are bearer-only, and they contain encrypted
        authentication information.
      </p>

      <p>
        They can be used as permanent or time-based tokens to authenticate
        with the Platypush API.
      </p>

      <p>
        When compared to the standard
        <a href="/#settings?page=tokens&type=api">API tokens</a>, JWT tokens
        have the following pros:
      </p>

      <ul>
        <li>They are not stored on the server, so compromising the server
          does not necessarily compromise the tokens too.</li>
      </ul>

      <p>
        And the following cons:
      </p>

      <ul>
        <li>They are not revocable - once generated, they can be used
          indefinitely until they expire.</li>
        <li>The only way to revoke a JWT token is to change the user's
          password. However, if a user changes their password, all the
          JWT tokens generated with the old password will be
          invalidated.</li>
        <li>Their payload is the encrypted representation of the user's
          credentials, but without any OTP information, so an attacker
          gains access to the user's credentials and the server's
          encryption keys they can impersonate the user indefinitely
          bypassing 2FA.</li>
      </ul>

      <p>
        For these reasons, it is recommended to use generic API tokens over JWT
        tokens for most use cases.<br/>
      </p>

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

export default {
  name: "Token",
  components: {
    Description,
    Loading,
    Modal,
  },
  mixins: [Utils],

  props: {
    currentUser: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      loading: false,
      requires2fa: this.currentUser?.has_2fa === true,
      token: null,
    }
  },

  methods: {
    async generateToken(event) {
      const username = this.currentUser.username
      const password = event.target.password.value
      const code = this.requires2fa ? event.target.code?.value : undefined
      let validityDays = event.target.validityDays?.length ? parseInt(event.target.validityDays.value) : 0
      if (!validityDays)
        validityDays = null

      this.loading = true
      try {
        const response = await axios.post('/auth?type=jwt', {
          username: username,
          password: password,
          code: code,
          expiry_days: validityDays,
        })

        this.token = response.data.token
        if (this.token?.length) {
          this.$refs.tokenParamsModal.close()
          this.$refs.tokenModal.show()
        }
      } catch (e) {
        console.error(e.toString())
        const error = e?.response?.data?.error

        if (error === 'MISSING_OTP_CODE') {
          this.requires2fa = true
          this.notify({
            text: e?.response?.data?.message || 'Please enter your OTP code.',
            error: true,
          })
          this.$nextTick(() => {
            this.$refs.code?.focus()
          })
        } else if (error === 'INVALID_OTP_CODE') {
          this.notify({
            text: e?.response?.data?.message || 'Invalid OTP code.',
            error: true,
          })
        } else if (error === 'INVALID_CREDENTIALS') {
          this.notify({
            text: e?.response?.data?.message || 'Invalid credentials.',
            error: true,
          })
        } else {
          this.notify({
            text: e?.response?.data?.message || e?.message || e?.toString(),
            error: true,
          })
        }
      } finally {
        this.loading = false
      }
    },
  }
}
</script>

<style lang="scss">
@import "style.scss";
</style>

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
           @open="$nextTick(() => $refs.password.focus())"
           @close="$refs.generateTokenForm.reset()">
      <div class="form-container">
        <p>Confirm your credentials in order to generate a new API token.</p>

        <form @submit.prevent="generateToken" ref="generateTokenForm">
          <label>
            <span>Confirm password</span>
            <span>
              <input type="password" name="password" ref="password" placeholder="Password">
            </span>
          </label>

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

    <div class="body">
      <label class="generate-btn-container">
        <button class="btn btn-primary" @click="$refs.tokenParamsModal.show()">
          Generate API Token
        </button>
      </label>

      <p>
        <b>API tokens</b> are randomly generated tokens that are stored
        encrypted on the server, and can be used to authenticate with the
        Platypush API.
      </p>

      <p>
        When compared to the
        <a href="/#settings?page=tokens&type=jwt">JWT tokens</a>, API tokens
        have the following advantages:

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
      </p>
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
  mixins: [Utils],
  components: {
    Description,
    Loading,
    Modal,
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
      token: null,
    }
  },

  methods: {
    async generateToken(event) {
      const username = this.currentUser.username
      const password = event.target.password.value
      const name = event.target.name.value
      let validityDays = event.target.validityDays?.length ? parseInt(event.target.validityDays.value) : 0
      if (!validityDays)
        validityDays = null

      this.loading = true
      try {
        this.token = (await axios.post('/auth?type=token', {
          username: username,
          password: password,
          name: name,
          expiry_days: validityDays,
        })).data.token

        if (this.token?.length)
          this.$refs.tokenModal.show()
      } catch (e) {
        console.error(e.toString())
        this.notify({
          text: e.toString(),
          error: true,
        })
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

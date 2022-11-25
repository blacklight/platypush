<template>
  <div class="token-container">
    <Loading v-if="loading" />

    <Modal ref="tokenModal">
      <div class="token-container">
        <label>
          This is your generated token. Treat it carefully and do not share it with untrusted parties.<br/>
          Also, make sure to save it - it WILL NOT be displayed again.

          <textarea class="token" v-text="token" @focus="onTokenSelect" />
        </label>
      </div>
    </Modal>

    <div class="body">
      <div class="description">
        <p>Generate a JWT authentication token that can be used for API calls to the <tt>/execute</tt> endpoint.</p><br/>
        <p>You can include the token in your requests in any of the following ways:</p>

        <ul>
          <li>Specify it on the <tt>Authorization: Bearer</tt> header;</li>
          <li>Specify it on the <tt>X-Token</tt> header;</li>
          <li>Specify it as a URL parameter: <tt>http://site:8008/execute?token=...</tt>;</li>
          <li>Specify it on the body of your JSON request: <tt>{"type":"request", "action", "...", "token":"..."}</tt>.</li>
        </ul>

        Confirm your credentials in order to generate a new token.
      </div>

      <div class="form-container">
        <form @submit.prevent="generateToken" ref="generateTokenForm">
          <label>
            <span>Username</span>
            <span>
              <input type="text" name="username" :value="currentUser.username" disabled>
            </span>
          </label>

          <label>
            <span>Confirm password</span>
            <span>
              <input type="password" name="password">
            </span>
          </label>

          <label>
            <span>Token validity in days</span>
            <span>
              <input type="text" name="validityDays">
            </span>
            <span class="note">
              Decimal values are also supported (e.g. <i>0.5</i> to identify 6 hours). An empty or zero value means that
              the token has no expiry date.
            </span>
          </label>

          <label>
            <input type="submit" class="btn btn-primary" value="Generate token">
          </label>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import Loading from "@/components/Loading";
import Utils from "@/Utils";
import Modal from "@/components/Modal";

export default {
  name: "Token",
  components: {Modal, Loading},
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
      token: null,
    }
  },

  methods: {
    async generateToken(event) {
      const username = this.currentUser.username
      const password = event.target.password.value
      let validityDays = event.target.validityDays?.length ? parseInt(event.target.validityDays.value) : 0
      if (!validityDays)
        validityDays = null

      this.loading = true
      try {
        this.token = (await axios.post('/auth', {
          username: username,
          password: password,
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

    onTokenSelect(event) {
      event.target.select()
      document.execCommand('copy')

      this.notify({
        text: 'Token copied to clipboard',
        image: {
          iconClass: 'fa fa-check',
        }
      })
    },
  }
}
</script>

<style lang="scss">
.token-container {
  width: 100%;
  display: flex;
  margin-top: .15em;

  .body {
    background: $background-color;
    display: flex;

    .description {
      text-align: left;
      padding: 1em;
    }
  }

  ul {
    margin: 1em .5em;

    li {
      list-style: initial;
    }
  }

  .form-container {
    display: flex;
  }

  form {
    max-width: 250pt;

    .note {
      display: block;
      font-size: .75em;
      margin: -.75em 0 2em 0;
    }

    span {
      input {
        width: 100%;
      }
    }
  }

  input[type=password] {
    border-radius: 1em;
  }

  .modal {
    .content {
      width: 90%;
    }

    .body {
      margin-top: 0;
    }
  }

  .token-container {
    label {
      display: flex;
      flex-direction: column;

      span {
        display: block;
        width: 100%;
      }
    }

    textarea {
      height: 10em;
      margin-top: 1em;
      border-radius: 1em;
    }
  }
}

@media screen and (max-width: calc(#{$desktop} - 1px)) {
  .token-container {
    .body {
      flex-direction: column;
    }
  }

  .form-container {
    justify-content: center;
    box-shadow: $border-shadow-top;
    margin-top: -1em;
    padding-top: 1em;
  }
}

@media screen and (min-width: $desktop) {
  .token-container {
    justify-content: center;
    align-items: center;

    .description {
      width: 50%;
    }

    .form-container {
      width: 50%;
      justify-content: right;
      padding: 1em;

      label {
        text-align: left;
      }
    }

    .body {
      max-width: 650pt;
      flex-direction: row;
      justify-content: left;
      margin-top: 1.5em;
      border-radius: 1em;
      border: $default-border-2;
    }
  }
}
</style>

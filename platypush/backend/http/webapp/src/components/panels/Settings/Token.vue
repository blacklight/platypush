<template>
  <div class="token-container">
    <Loading v-if="loading" />

    <Modal ref="tokenModal">
      <div class="token-container">
        <label>
          This is your generated token. Treat it carefully and do not share it with untrusted parties.<br/>
          Also, make sure to save it - it WILL NOT be displayed again.
        </label>

        <textarea class="token" v-text="token" @focus="onTokenSelect" />
      </div>
    </Modal>

    <Modal ref="sessionTokenModal">
      <div class="token-container">
        <label>
          This is your current session token.
          It will be invalidated once you log out of the current session.
        </label>

        <textarea class="token" v-text="sessionToken" @focus="onTokenSelect" />
      </div>
    </Modal>

    <div class="body">
      <div class="description">
        <p>
          Platypush provides two types of tokens:

          <ul>
            <li>
              <b>JWT tokens</b> are bearer-only, and they contain encrypted
              authentication information.<br/>
              They can be used as permanent or time-based tokens to
              authenticate with the Platypush API.
            </li>

            <li>
              <b>Session tokens</b> are randomly generated tokens stored on the
              application database. A session token generated in this session
              will expire when you log out of it.
            </li>
          </ul>
        </p>

        <p>Generate a JWT authentication token that can be used for API calls to the <code>/execute</code> endpoint.</p><br/>
        <p>You can include the token in your requests in any of the following ways:</p>

        <ul>
          <li>Specify it on the <code>Authorization: Bearer</code> header;</li>
          <li>Specify it on the <code>X-Token</code> header;</li>
          <li>
            Specify it as a URL parameter: <code>http://site:8008/execute?token=...</code>
            for a JWT token and <code>...?session_token=...</code> for a
            session token;
          </li>
          <li>Specify it on the body of your JSON request:
            <code>{"type":"request", "action", "...", "token":"..."}</code> for
            a JWT token, or <code>"session_token"</code> for a session token.
          </li>
        </ul>

        <p>Confirm your credentials in order to generate a new JWT token.</p>
        <p>
          <i>Show session token</i> will instead show the token cookie associated
          to the current session.
        </p>
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
              Decimal values are also supported - e.g. <i>0.5</i> means half a
              day (12 hours). An empty or zero value means that the token has
              no expiry date.
            </span>
          </label>

          <label>
            <input type="submit" class="btn btn-primary" value="Generate JWT token">
          </label>

          <label>
            <input type="button" class="btn btn-default" value="Show session token"
              @click.stop="$refs.sessionTokenModal.show()">
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

    sessionToken: {
      type: String,
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
  flex-direction: column;
  margin-top: .15em;

  label {
    width: 100%;
  }

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
      width: 100%;
      height: 10em;
      margin-top: 1em;
      border-radius: 1em;
      border: none;
      background: $active-glow-bg-1;
      padding: 1em;
    }
  }

  .btn {
    border-radius: 1em;
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

<template>
  <div class="login-container">
    <form class="login" method="POST">
      <div class="description">
        {{ _register ? 'Welcome' : 'Authenticate' }} to platypush
      </div>

      <div class="row">
        <label>
          <input type="text" name="username" placeholder="Username">
        </label>
      </div>

      <div class="row">
        <label>
          <input type="password" name="password" placeholder="Password">
        </label>
      </div>

      <div class="row" v-if="_register">
        <label>
          <input type="password" name="confirm_password" placeholder="Confirm password">
        </label>
      </div>

      <div class="row pull-right">
        <input type="submit" class="btn btn-primary" :value="_register ? 'Register' : 'Login'">
      </div>

      <div class="row pull-right">
        <label class="checkbox">
          <input type="checkbox" name="remember">&nbsp;
          Keep me logged in on this device &nbsp;
        </label>
      </div>
    </form>
  </div>
</template>

<script>
import Utils from "@/Utils";

export default {
  name: "Login",
  mixins: [Utils],
  props: {
    // Set to true for a registration form, false for a login form
    register: {
      type: Boolean,
      required: false,
      default: false,
    },
  },

  computed: {
    _register() {
      return this.parseBoolean(this.register)
    },
  }
}
</script>

<style lang="scss">
body {
  width: 100vw;
  height: 100vh;
  margin: 0;
  overflow-x: hidden;
}

.login-container {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.description {
  margin-bottom: 2em;
  text-align: center;
}

form {
  display: flex;
  flex-direction: column;
  padding: 4em;
  border: $default-border-3;
  border-radius: 3em;
  box-shadow: 2px 2px 3px 3px $border-color-2;

  .row {
    margin: 0.5em 0;
  }

  input[type=text],
  input[type=password] {
    width: 100%;
  }

  input[type=submit] {
    border-radius: 1em;
  }

  .checkbox {
    display: flex;
    font-size: 0.8em;
  }
}

a {
  color: $default-link-fg;
}
</style>

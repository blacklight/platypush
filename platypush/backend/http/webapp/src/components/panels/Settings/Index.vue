<template>
  <div class="settings-container">
    <main>
      <Application v-if="selectedPanel === 'application'" />
      <Users :session-token="sessionToken" :current-user="currentUser"
             v-if="selectedPanel === 'users' && currentUser" />
      <Tokens :current-user="currentUser"
              v-else-if="selectedPanel === 'tokens' && currentUser" />
    </main>
  </div>
</template>

<script>
import Application from "@/components/panels/Settings/Application";
import Tokens from "@/components/panels/Settings/Tokens/Index";
import Users from "@/components/panels/Settings/Users";
import Utils from "@/Utils";

export default {
  name: "Settings",
  components: {Application, Users, Tokens},
  mixins: [Utils],
  emits: ['change-page'],

  props: {
    selectedPanel: {
      type: String,
    },
  },

  data() {
    return {
      currentUser: null,
      sessionToken: null,
    }
  },

  methods: {
    async refresh() {
      this.sessionToken = this.getCookies()['session_token']
      this.currentUser = await this.request('user.get_user_by_session', {session_token: this.sessionToken})
    },

    updatePage() {
      const args = this.getUrlArgs()
      let page = null
      if (args.page?.length) {
        page = args.page
      } else {
        page = this.selectedPanel?.length ? this.selectedPanel : 'users'
      }

      this.$emit('change-page', page)
    },
  },

  watch: {
    selectedPanel(value) {
      this.setUrlArgs({page: value})
    },

    $route() {
      this.updatePage()
    },
  },

  async mounted() {
    this.updatePage()
    await this.refresh()
  }
}
</script>

<style lang="scss" scoped>
$header-height: 3em;

.settings-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;

  header {
    width: 100%;
    height: $header-height;
    display: flex;
    background: $background-color;
    box-shadow: $border-shadow-bottom;
    padding: .5em;

    select {
      width: 100%;
    }

    button {
      padding-top: .25em;
    }
  }

  @include until($tablet) {
    main {
      height: calc(100% - #{$header-height});
      overflow: auto;
    }
  }

  @include from($tablet) {
    main {
      height: 100%;
    }
  }

  button {
    background: none;
  }

  form {
    padding: 0;
    border: none;
    border-radius: 0;
    box-shadow: none;

    input {
      margin-bottom: 1em;
    }
  }

  input[type=password] {
    border-radius: 1em;
  }
}
</style>

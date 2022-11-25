<template>
  <div class="settings-container">
    <header>
      <div class="col-8">
        <Dropdown title="Select a category" icon-class="fa fa-ellipsis-h">
          <DropdownItem text="Users" icon-class="fa fa-user"
            :item-class="{selected: selectedView === 'users'}"
            @click="selectedView = 'users'" />
          <DropdownItem text="Generate a token" icon-class="fa fa-key"
            :item-class="{selected: selectedView === 'token'}"
            @click="selectedView = 'token'" />
        </Dropdown>
      </div>

      <div class="col-4 pull-right">
        <button title="Add User" @click="$refs.usersView.$refs.addUserModal.show()" v-if="selectedView === 'users'">
          <i class="fa fa-plus" />
        </button>
      </div>
    </header>

    <main>
      <Users :session-token="sessionToken" :current-user="currentUser"
             v-if="selectedView === 'users'" ref="usersView" />
      <Token :session-token="sessionToken" :current-user="currentUser"
             v-else-if="selectedView === 'token'" ref="tokenView" />
    </main>
  </div>
</template>

<script>
import Dropdown from "@/components/elements/Dropdown";
import DropdownItem from "@/components/elements/DropdownItem";
import Token from "@/components/panels/Settings/Token";
import Users from "@/components/panels/Settings/Users";
import Utils from "@/Utils";

export default {
  name: "Settings",
  components: {Dropdown, DropdownItem, Users, Token},
  mixins: [Utils],

  data() {
    return {
      selectedView: 'users',
      currentUser: null,
      sessionToken: null,
    }
  },

  methods: {
    async refresh() {
      this.sessionToken = this.getCookies()['session_token']
      this.currentUser = await this.request('user.get_user_by_session', {session_token: this.sessionToken})
    }
  },

  mounted() {
    this.refresh()
  }
}
</script>

<style lang="scss">
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

  main {
    height: calc(100% - #{$header-height});
    overflow: auto;
  }

  button {
    background: none;
    border: none;

    &:hover {
      border: none;
      color: $default-hover-fg;
    }
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

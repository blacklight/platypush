<template>
  <Loading v-if="loading" />

  <Modal ref="addUserModal" title="Add User">
    <form action="#" method="POST" ref="addUserForm" @submit="createUser">
      <label>
        <input type="text" name="username" placeholder="Username" :disabled="commandRunning">
      </label>
      <label>
        <input type="password" name="password" placeholder="Password" :disabled="commandRunning">
      </label>
      <label>
        <input type="password" name="confirm_password" placeholder="Confirm password" :disabled="commandRunning">
      </label>
      <label>
        <input type="submit" class="btn btn-primary" value="Create User" :disabled="commandRunning">
      </label>
    </form>
  </Modal>

  <Modal ref="changePasswordModal" title="Change Password">
    <form action="#" method="POST" ref="changePasswordForm" @submit="changePassword">
      <label>
        <input type="text" name="username" placeholder="Username" :value="selectedUser" disabled="disabled">
      </label>
      <label>
        <input type="password" name="password" placeholder="Current password" :disabled="commandRunning">
      </label>
      <label>
        <input type="password" name="new_password" placeholder="New password" :disabled="commandRunning">
      </label>
      <label>
        <input type="password" name="confirm_new_password" placeholder="Confirm new password" :disabled="commandRunning">
      </label>
      <label>
        <input type="submit" class="btn btn-primary" value="Change Password" :disabled="commandRunning">
      </label>
    </form>
  </modal>

  <div class="body">
    <ul class="users-list">
      <li v-for="user in users" :key="user.user_id" class="item user" @click="selectedUser = user.username">
        <div class="name col-8" v-text="user.username" />
        <div class="actions pull-right col-4">
          <Dropdown title="User Actions" icon-class="fa fa-ellipsis">
            <DropdownItem text="Change Password" :disabled="commandRunning" icon-class="fa fa-key"
                          @click="showChangePasswordModal(user)" />
            <DropdownItem text="Delete User" :disabled="commandRunning" icon-class="fa fa-trash"
                          @click="selectedUser = user.username; $refs.deleteUserDialog.show()" />
          </Dropdown>
        </div>
      </li>
    </ul>

    <FloatingButton icon-class="fa fa-plus" text="Add User" @click="showAddUserModal" />

    <ConfirmDialog ref="deleteUserDialog" @input="deleteUser(selectedUser)">
      Are you sure that you want to remove the user {{ selectedUser }}?
    </ConfirmDialog>
  </div>
</template>

<script>
import ConfirmDialog from "@/components/elements/ConfirmDialog";
import Dropdown from "@/components/elements/Dropdown";
import Modal from "@/components/Modal";
import Loading from "@/components/Loading";
import Utils from "@/Utils";
import DropdownItem from "@/components/elements/DropdownItem";
import FloatingButton from "@/components/elements/FloatingButton";

export default {
  name: "Users",
  components: {ConfirmDialog, Dropdown, DropdownItem, FloatingButton, Loading, Modal},
  mixins: [Utils],

  props: {
    sessionToken: {
      type: String,
      required: true,
    },

    currentUser: {
      type: Object,
      required: true,
    }
  },

  data() {
    return {
      users: [],
      commandRunning: false,
      loading: false,
      selectedUser: null,
    }
  },

  methods: {
    async refresh() {
      this.loading = true
      try {
        this.users = await this.request('user.get_users')
      } finally {
        this.loading = false
      }
    },

    async createUser(event) {
      event.preventDefault()

      const form = [...this.$refs.addUserForm.querySelectorAll('input[name]')].reduce((map, input) => {
        map[input.name] = input.value
        return map
      }, {})

      if (form.password !== form.confirm_password) {
        this.notify({
          title: 'Unable to create user',
          text: 'Please check that the passwords match',
          error: true,
          image: {
            iconClass: 'fas fa-times',
          },
        })

        return
      }

      this.commandRunning = true
      try {
        await this.request('user.create_user', {
          username: form.username,
          password: form.password,
          session_token: this.sessionToken,
        })
      } finally {
        this.commandRunning = false
      }

      this.notify({
        text: 'User ' + form.username + ' created',
        image: {
          iconClass: 'fas fa-check',
        },
      })

      this.$refs.addUserModal.close()
      await this.refresh()
    },

    async changePassword(event) {
      event.preventDefault()

      const form = [...this.$refs.changePasswordForm.querySelectorAll('input[name]')].reduce((map, input) => {
        map[input.name] = input.value
        return map
      }, {})

      if (form.new_password !== form.confirm_new_password) {
        this.notify({
          title: 'Unable to update password',
          text: 'Please check that the passwords match',
          error: true,
          image: {
            iconClass: 'fas fa-times',
          },
        })

        return
      }

      this.commandRunning = true
      let success = false

      try {
        success = await this.request('user.update_password', {
          username: form.username,
          old_password: form.password,
          new_password: form.new_password,
        })
      } finally {
        this.commandRunning = false
      }

      if (success) {
        this.$refs.changePasswordModal.close()
        this.notify({
          text: 'Password successfully updated',
          image: {
            iconClass: 'fas fa-check',
          },
        })
      } else {
        this.notify({
          title: 'Unable to update password',
          text: 'The current password is incorrect',
          error: true,
          image: {
            iconClass: 'fas fa-times',
          },
        })
      }
    },

    async deleteUser(user) {
      this.commandRunning = true
      try {
        await this.request('user.delete_user', {
          username: user,
          session_token: this.sessionToken,
        })
      } finally {
        this.commandRunning = false
      }

      this.notify({
        text: `User ${user} removed`,
        image: {
          iconClass: 'fas fa-check',
        },
      })

      this.selectedUser = null
      await this.refresh()
    },

    showAddUserModal() {
      this.$refs.addUserModal.show()
      this.$nextTick(() => {
        this.$refs.addUserForm.reset()
        this.$refs.addUserForm.username.focus()
      })
    },

    showChangePasswordModal(user) {
      this.$refs.changePasswordModal.show()
      this.$nextTick(() => {
        this.$refs.changePasswordForm.password.focus()
        this.selectedUser = user.username
      })
    },
  },

  mounted() {
    this.refresh()
  },
}
</script>

<style lang="scss" scoped>
.settings-container {
  .body {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
  }

  .modal {
    .body {
      height: auto;
    }
  }

  form {
    label {
      display: block;
      text-align: center;
    }
  }

  .users-list {
    background: $background-color;
    margin-top: .15em;
    height: max-content;

    .user {
      display: flex;
      align-items: center;
      padding: .75em;

      &:not(:last-child) {
        box-shadow: $border-shadow-bottom;
      }

      &:hover {
        background: $hover-bg;
      }

      .actions {
        display: inline-flex;
        justify-content: right;

        button {
          background: none !important;
          width: min-content;
        }
      }
    }
  }

  @media screen and (max-width: $desktop) {
    .users-list {
      width: 100%;
    }
  }

  @media screen and (min-width: $desktop) {
    .users-list {
      min-width: 400pt;
      max-width: 600pt;
      margin-top: 1em;
      border-radius: 1em;
      box-shadow: $border-shadow-bottom;

      .user {
        border-radius: 0;

        &:first-child {
          border-top-left-radius: 1em;
          border-top-right-radius: 1em;
        }

        &:last-child {
          border-bottom-left-radius: 1em;
          border-bottom-right-radius: 1em;
        }
      }
    }
  }
}

:deep(.dropdown-container) {
  button {
    background: none !important;
  }
}

:deep(.modal) {
  .btn {
    border-radius: 1em;
  }
}
</style>

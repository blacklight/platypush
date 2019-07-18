window.vm = new Vue({
    el: '#app',
    data: function() {
        return {
            config: window.config,
            sessionToken: undefined,
            selectedTab: 'users',
            selectedUser: undefined,

            modalVisible: {
                addUser: false,
                changePassword: false,
            },

            formDisabled: {
                addUser: false,
                changePassword: false,
            },
        };
    },

    computed: {
        userDropdownItems: function() {
            const self = this;
            return [
                {
                    text: 'Change password',
                    iconClass: 'fas fa-key',
                    click: function() {
                        self.modalVisible.changePassword = true;
                    },
                },
                {
                    text: 'Delete user',
                    iconClass: 'fa fa-trash',
                    click: async function() {
                        if (!confirm('Are you sure that you want to remove the user ' + self.selectedUser + '?'))
                            return;

                        await request('user.delete_user', {
                            username: self.selectedUser,
                            session_token: self.sessionToken,
                        });

                        createNotification({
                            text: 'User ' + self.selectedUser + ' removed',
                            image: {
                                iconClass: 'fas fa-check',
                            },
                        });

                        window.location.reload();
                    },
                },
            ];
        },
    },

    methods: {
        createUser: async function(event) {
            event.preventDefault();

            let form = [...this.$refs.createUserForm.querySelectorAll('input[name]')].reduce((map, input) => {
                map[input.name] = input.value;
                return map;
            }, {});

            if (form.password != form.confirm_password) {
                createNotification({
                    text: 'Please check that the passwords match',
                    image: {
                        iconClass: 'fas fa-times',
                    },
                    error: true,
                });

                return;
            }

            this.formDisabled.addUser = true;
            await request('user.create_user', {
                username: form.username,
                password: form.password,
                session_token: this.sessionToken,
            });

            this.formDisabled.addUser = false;
            createNotification({
                text: 'User ' + form.username + ' created',
                image: {
                    iconClass: 'fas fa-check',
                },
            });

            this.modalVisible.addUser = false;
            window.location.reload();
        },

        onUserClick: function(username) {
            this.selectedUser = username;
            openDropdown(this.$refs.userDropdown.$el);
        },

        onTokenFocus: function(event) {
            event.target.select();
            document.execCommand('copy');
            event.target.setAttribute('disabled', true);

            createNotification({
                text: 'Token copied to clipboard',
                image: {
                    iconClass: 'fas fa-copy',
                },
            });
        },

        onTokenBlur: function(event) {
            event.target.select();
            document.execCommand('copy');
            event.target.removeAttribute('disabled');

            createNotification({
                text: 'Token copied to clipboard',
                image: {
                    iconClass: 'fas fa-copy',
                },
            });
        },

        changePassword: async function(event) {
            event.preventDefault();

            let form = [...this.$refs.changePasswordForm.querySelectorAll('input[name]')].reduce((map, input) => {
                map[input.name] = input.value;
                return map;
            }, {});

            if (form.new_password !== form.confirm_new_password) {
                createNotification({
                    text: 'Please check that the passwords match',
                    image: {
                        iconClass: 'fas fa-times',
                    },
                    error: true,
                });

                return;
            }

            this.formDisabled.changePassword = true;
            let success = await request('user.update_password', {
                username: form.username,
                old_password: form.password,
                new_password: form.new_password,
            });

            this.formDisabled.changePassword = false;

            if (success) {
                this.modalVisible.changePassword = false;
                createNotification({
                    text: 'Password successfully updated',
                    image: {
                        iconClass: 'fas fa-check',
                    },
                });
            } else {
                createNotification({
                    text: 'Unable to update password: the current password is incorrect',
                    image: {
                        iconClass: 'fas fa-times',
                    },
                    error: true,
                });
            }
        },
    },

    created: function() {
        let cookies = Object.fromEntries(document.cookie.split('; ').map(x => x.split('=')));
        this.sessionToken = cookies.session_token;
    },
});


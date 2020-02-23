Vue.component('zigbee-device', {
    template: '#tmpl-zigbee-device',
    props: ['device','bus','selected'],
    data: function() {
        return {
            newPropertyName: '',
            editMode: {
                name: false,
            },
        };
    },

    methods: {
        onDeviceClicked: function() {
            this.bus.$emit('deviceClicked', {
                deviceId: this.device.friendly_name,
            });
        },

        setValue: async function(event) {
            let name = undefined;
            if (this.newPropertyName && this.newPropertyName.length) {
                name = this.newPropertyName;
            } else {
                name = event.event
                    ? event.event.target.parentElement.dataset.name
                    : event.target.dataset.name;
            }

            if (!name || !name.length) {
                return;
            }

            const target = event.event
                ? event.event.target.parentElement.querySelector('input')
                : event.target;

            const value = target.getAttribute('type') === 'checkbox'
                ? (target.checked ? 'OFF' : 'ON')
                : target.value;

            await request('zigbee.mqtt.device_set', {
                device: this.device.friendly_name,
                property: name,
                value: value,
            });

            if (this.newPropertyName && this.newPropertyName.length) {
                this.newPropertyName = '';
            }

            this.bus.$emit('refreshDevices');
        },

        removeDevice: async function(force=false) {
            if (!confirm('Are you sure that you want to remove this device?')) {
                return;
            }

            await request('zigbee.mqtt.device_remove', {
                device: this.device.friendly_name,
                force: force,
            });

            this.bus.$emit('refreshDevices');
        },

        banDevice: async function() {
            if (!confirm('Are you sure that you want to ban this device?')) {
                return;
            }

            await request('zigbee.mqtt.device_ban', {
                device: this.device.friendly_name,
            });

            this.bus.$emit('refreshDevices');
        },

        whitelistDevice: async function() {
            if (!confirm('Are you sure that you want to whitelist this device? Note: ALL the other non-whitelisted ' +
                    'devices will be removed from the network')) {
                return;
            }

            await request('zigbee.mqtt.device_whitelist', {
                device: this.device.friendly_name,
            });

            this.bus.$emit('refreshDevices');
        },

        disableForm: function(form) {
            form.querySelector('input,button').readOnly = true;
        },

        enableForm: function(form) {
            form.querySelector('input,button').readOnly = false;
        },

        onEditMode: function(mode) {
            Vue.set(this.editMode, mode, true);
            const form = this.$refs[mode + 'Form'];
            const input = form.querySelector('input[type=text]');

            setTimeout(() => {
                input.focus();
                input.select();
            }, 10);
        },

        editName: async function(event) {
            this.disableForm(event.target);
            const name = event.target.querySelector('input[name=name]').value;

            await request('zigbee.mqtt.device_rename', {
                device: this.device.friendly_name,
                name: name,
            });

            this.editMode.name = false;
            this.enableForm(event.target);
            this.bus.$emit('refreshDevices');
        },
    },
});


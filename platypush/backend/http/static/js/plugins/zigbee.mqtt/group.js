Vue.component('zigbee-group', {
    template: '#tmpl-zigbee-group',
    props: ['group','bus','selected'],
    data: function() {
        return {
            properties: {},
        };
    },

    methods: {
        anyOn: async function() {
            for (const dev of this.group.devices) {
                const params = await request('zigbee.mqtt.device_get', {device: dev.friendly_name});
                if (params.state === 'ON') {
                    return true;
                }
            }

            return false;
        },

        allOn: async function() {
            for (const dev of this.group.devices) {
                const params = await request('zigbee.mqtt.device_get', {device: dev.friendly_name});
                if (params.state === 'OFF') {
                    return false;
                }
            }

            return true;
        },

        refreshProperties: async function() {
            const props = {};

            for (const dev of this.group.devices) {
                const params = await request('zigbee.mqtt.device_get', {device: dev.friendly_name});
                for (const [name, value] of Object.entries(params)) {
                    if (name === 'linkquality') {
                        continue;
                    }

                    if (name in props) {
                        props[name].push(value);
                    } else {
                        props[name] = [value];
                    }
                }
            }

            for (const [name, values] of Object.entries(props)) {
                if (name === 'state') {
                    props[name] = values.filter((value) => value === 'ON').length > 0;
                } else if (!isNaN(values[0])) {
                    props[name] = values.reduce((sum, value) => sum + value, 0) / values.length;
                } else {
                    props[name] = values[0];
                }
            }

            this.properties = props;
        },

        onGroupClicked: function() {
            this.bus.$emit('groupClicked', {
                groupId: this.group.id,
            });
        },

        setValue: async function(event) {
            const name = event.target.dataset.name;
            if (!name || !name.length) {
                return;
            }

            await request('zigbee.mqtt.group_set', {
                group: this.group.friendly_name,
                property: name,
                value: event.target.value,
            });

            this.bus.$emit('refreshDevices');
        },

        toggleState: async function() {
            const state = (await this.anyOn()) ? 'OFF' : 'ON';
            await request('zigbee.mqtt.group_set', {
                group: this.group.friendly_name,
                property: 'state',
                value: state,
            });

            this.bus.$emit('refreshDevices');
        },

        renameGroup: async function() {
            const name = prompt('New name', this.group.friendly_name);
            if (!name || !name.length || name === this.group.friendly_name) {
                return;
            }

            this.commandRunning = true;
            await request('zigbee.mqtt.group_rename', {
                name: name,
                group: this.group.friendly_name,
            });

            this.commandRunning = false;
            const self = this;

            setTimeout(() => {
                self.bus.$emit('refreshGroups');
            }, 100);
        },

        removeGroup: async function() {
            if (!confirm('Are you sure that you want to delete this group?')) {
                return;
            }

            this.commandRunning = true;
            await request('zigbee.mqtt.group_remove', {name: this.group.friendly_name});
            this.commandRunning = false;
            this.bus.$emit('refreshGroups');
        },

        removeFromGroup: async function(device) {
            if (!confirm('Are you sure that you want to remove this node from ' + this.group.label + '?')) {
                return;
            }

            await request('zigbee.mqtt.group_remove_device', {
                device: device,
                group: this.group.friendly_name,
            });

            this.bus.$emit('refreshGroups');
        },
    },

    created: function() {
        this.refreshProperties();
        this.bus.$on('refresh', this.refreshProperties);
        this.bus.$on('refreshDevices', this.refreshProperties);
        this.bus.$on('refreshGroups', this.refreshProperties);
        this.bus.$on('refreshProperties', this.refreshProperties);
    },
});


Vue.component('zigbee-mqtt', {
    template: '#tmpl-zigbee-mqtt',
    props: ['config'],

    data: function() {
        return {
            bus: new Vue({}),
            status: {},
            devices: {},
            groups: {},
            commandRunning: false,
            selected: {
                view: 'devices',
                deviceId: undefined,
                groupId: undefined,
            },
            loading: {
                status: false,
                devices: false,
                groups: false,
            },
            views: {
                devices: true,
                groups: true,
            },
            modal: {
                group: {
                    visible: false,
                },
            },
        };
    },

    computed: {
        networkDropdownItems: function() {
            const self = this;
            return [
                {
                    text: 'Start Network',
                    disabled: this.commandRunning,
                    click: async function() {
                        self.commandRunning = true;
                        await request('zigbee.mqtt.start_network');
                        self.commandRunning = false;
                    },
                },

                {
                    text: 'Stop Network',
                    disabled: this.commandRunning,
                    click: async function() {
                        self.commandRunning = true;
                        await request('zigbee.mqtt.stop_network');
                        self.commandRunning = false;
                    },
                },

                {
                    text: 'Permit Join',
                    disabled: this.commandRunning,
                    click: async function() {
                        let seconds = prompt('Join allow period in seconds (type 0 for no time limits)', '60');
                        if (!seconds) {
                            return;
                        }

                        seconds = parseInt(seconds);
                        self.commandRunning = true;
                        await request('zigbee.mqtt.permit_join', {permit: true, timeout: seconds || null});
                        self.commandRunning = false;
                    },
                },

                {
                    text: 'Reset',
                    disabled: this.commandRunning,
                    click: async function() {
                        if (!confirm('Are you sure that you want to reset the device?')) {
                            return;
                        }

                        await request('zigbee.mqtt.reset');
                    },
                },

                {
                    text: 'Factory Reset',
                    disabled: this.commandRunning,
                    classes: ['error'],
                    click: async function() {
                        if (!confirm('Are you sure that you want to do a device soft reset? ALL network information and custom firmware will be lost!!')) {
                            return;
                        }

                        await request('zigbee.mqtt.factory_reset');
                    },
                },
            ]
        },

        addToGroupDropdownItems: function() {
            const self = this;
            return Object.values(this.groups).filter((group) => {
                return !group.values || !group.values.length || !(this.selected.valueId in this.scene.values);
            }).map((group) => {
                return {
                    text: group.name,
                    disabled: this.commandRunning,
                    click: async function () {
                        if (!self.selected.valueId) {
                            return;
                        }

                        self.commandRunning = true;
                        await request('zwave.scene_add_value', {
                            id_on_network: self.selected.valueId,
                            scene_id: group.scene_id,
                        });

                        self.commandRunning = false;
                        self.refresh();
                    },
                };
            });
        },
    },

    methods: {
        refreshDevices: async function () {
            const self = this;
            this.loading.devices = true;
            this.devices = (await request('zigbee.mqtt.devices')).reduce((devices, device) => {
                if (device.friendly_name in self.devices) {
                    device = {
                        values: self.devices[device.friendly_name].values || {},
                        ...self.devices[device.friendly_name],
                    }
                }

                devices[device.friendly_name] = device;
                return devices;
            }, {});

            Object.values(this.devices).forEach((device) => {
                if (device.type === 'Coordinator') {
                    return;
                }

                request('zigbee.mqtt.device_get', {device: device.friendly_name}).then((response) => {
                    Vue.set(self.devices[device.friendly_name], 'values', response || {});
                });
            });

            this.loading.devices = false;
        },

        refreshGroups: async function () {
            this.loading.groups = true;
            this.groups = (await request('zigbee.mqtt.groups')).reduce((groups, group) => {
                groups[group.id] = group;
                return groups;
            }, {});

            this.loading.groups = false;
        },

        refresh: function () {
            this.refreshDevices();
            this.refreshGroups();
            this.bus.$emit('refreshProperties');
        },

        updateProperties: function(device, props) {
            Vue.set(this.devices[device], 'values', props);
        },

        addGroup: async function() {
            const name = prompt('Group name');
            if (!name) {
                return;
            }

            this.commandRunning = true;
            await request('zigbee.mqtt.group_add', {name: name});
            this.commandRunning = false;
            this.refreshGroups();
        },

        onViewChange: function(event) {
            Vue.set(this.selected, 'view', event.target.value);
        },

        onDeviceClicked: function(event) {
            Vue.set(this.selected, 'deviceId', event.deviceId === this.selected.deviceId ? undefined : event.deviceId);
        },

        onGroupClicked: function(event) {
            Vue.set(this.selected, 'groupId', event.groupId === this.selected.groupId ? undefined : event.groupId);
        },

        openNetworkCommandsDropdown: function() {
            openDropdown(this.$refs.networkCommandsDropdown);
        },

        openAddToGroupDropdown: function(event) {
            this.selected.valueId = event.valueId;
            openDropdown(this.$refs.addToGroupDropdown);
        },

        addToGroup: async function(device, group) {
            this.commandRunning = true;
            await request('zigbee.mqtt.group_add_device', {
                device: device,
                group: group,
            });

            this.commandRunning = false;
            const self = this;

            setTimeout(() => {
                self.refresh();
                self.bus.$emit('refreshProperties');
            }, 100)
        },

        removeNodeFromGroup: async function(event) {
            if (!confirm('Are you sure that you want to remove this value from the group?')) {
                return;
            }

            this.commandRunning = true;
            await request('zigbee.mqtt.group_remove_device', {
                group: event.group,
                device: event.device,
            });

            this.commandRunning = false;
        },
    },

    created: function() {
        const self = this;
        this.bus.$on('refresh', this.refresh);
        this.bus.$on('refreshDevices', this.refreshDevices);
        this.bus.$on('refreshGroups', this.refreshGroups);
        this.bus.$on('deviceClicked', this.onDeviceClicked);
        this.bus.$on('groupClicked', this.onGroupClicked);
        this.bus.$on('openAddToGroupModal', () => {self.modal.group.visible = true});
        this.bus.$on('openAddToGroupDropdown', this.openAddToGroupDropdown);
        this.bus.$on('removeFromGroup', this.removeNodeFromGroup);

        registerEventHandler(() => {
            createNotification({
                text: 'WARNING: The controller is now offline',
                error: true,
            });
        }, 'platypush.message.event.zigbee.mqtt.ZigbeeMqttOfflineEvent');

        registerEventHandler(() => {
            createNotification({
                text: 'The controller is now online',
                iconClass: 'fas fa-check',
            });
        }, 'platypush.message.event.zigbee.mqtt.ZigbeeMqttOfflineEvent');

        registerEventHandler(() => {
            createNotification({
                text: 'Failed to remove the device',
                error: true,
            });
        }, 'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceRemovedFailedEvent');

        registerEventHandler(() => {
            createNotification({
                text: 'Failed to add the group',
                error: true,
            });
        }, 'platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupAddedFailedEvent');

        registerEventHandler(() => {
            createNotification({
                text: 'Failed to remove the group',
                error: true,
            });
        }, 'platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupRemovedFailedEvent');

        registerEventHandler(() => {
            createNotification({
                text: 'Failed to remove the devices from the group',
                error: true,
            });
        }, 'platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupRemoveAllFailedEvent');

        registerEventHandler((event) => {
            createNotification({
                text: 'Unhandled Zigbee error: ' + (event.error || '[Unknown error]'),
                error: true,
            });
        }, 'platypush.message.event.zigbee.mqtt.ZigbeeMqttErrorEvent');

        registerEventHandler((event) => {
            self.updateProperties(event.device, event.properties);
        }, 'platypush.message.event.zigbee.mqtt.ZigbeeMqttDevicePropertySetEvent');

        registerEventHandler(this.refresh,
            'platypush.message.event.zigbee.mqtt.ZigbeeMqttOnlineEvent',
            'platypush.message.event.zigbee.mqtt.ZigbeeMqttDevicePairingEvent',
            'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceConnectedEvent',
            'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceBannedEvent',
            'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceRemovedEvent',
            'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceWhitelistedEvent',
            'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceRenamedEvent',
            'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceBindEvent',
            'platypush.message.event.zigbee.mqtt.ZigbeeMqttDeviceUnbindEvent',
            'platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupAddedEvent',
            'platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupRemovedEvent',
            'platypush.message.event.zigbee.mqtt.ZigbeeMqttGroupRemoveAllEvent',
        );
    },

    mounted: function() {
        this.refresh();
    },
});


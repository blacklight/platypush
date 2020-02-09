Vue.component('zwave', {
    template: '#tmpl-zwave',
    props: ['config'],

    data: function() {
        return {
            bus: new Vue({}),
            status: {},
            views: {},
            nodes: {},
            groups: {},
            scenes: {},
            values: {},
            switches: new Set(),
            dimmers: new Set(),
            sensors: new Set(),
            batteryLevels: new Set(),
            powerLevels: new Set(),
            bulbs: new Set(),
            doorlocks: new Set(),
            usercodes: new Set(),
            thermostats: new Set(),
            protections: new Set(),
            commandRunning: false,
            selected: {
                view: 'nodes',
                nodeId: undefined,
                groupId: undefined,
                sceneId: undefined,
                valueId: undefined,
            },
            loading: {
                status: false,
                nodes: false,
                groups: false,
                scenes: false,
                values: false,
            },
            modal: {
                networkInfo: {
                    visible: false,
                },
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
                        await request('zwave.start_network');
                        self.commandRunning = false;
                    },
                },

                {
                    text: 'Stop Network',
                    disabled: this.commandRunning,
                    click: async function() {
                        self.commandRunning = true;
                        await request('zwave.start_network');
                        self.commandRunning = false;
                    },
                },

                {
                    text: 'Switch All On',
                    disabled: this.commandRunning,
                    click: async function() {
                        self.commandRunning = true;
                        await request('zwave.switch_all', {state: true});
                        self.commandRunning = false;
                        self.refresh();
                    },
                },

                {
                    text: 'Switch All Off',
                    disabled: this.commandRunning,
                    click: async function() {
                        self.commandRunning = true;
                        await request('zwave.switch_all', {state: false});
                        self.commandRunning = false;
                        self.refresh();
                    },
                },

                {
                    text: 'Cancel Command',
                    click: async function() {
                        await request('zwave.cancel_command');
                    },
                },

                {
                    text: 'Kill Command',
                    click: async function() {
                        await request('zwave.kill_command');
                    },
                },

                {
                    text: 'Set Controller Name',
                    disabled: this.commandRunning,
                    click: async function() {
                        const name = prompt('Controller name');
                        if (!name) {
                            return;
                        }

                        self.commandRunning = true;
                        await request('zwave.set_controller_name', {name: name});
                        self.commandRunning = false;
                        self.refresh();
                    },
                },


                {
                    text: 'Receive Configuration From Primary',
                    disabled: this.commandRunning,
                    click: async function() {
                        self.commandRunning = true;
                        await request('zwave.receive_configuration');
                        self.commandRunning = false;
                        self.refresh();
                    },
                },

                {
                    text: 'Create New Primary',
                    disabled: this.commandRunning,
                    click: async function() {
                        self.commandRunning = true;
                        await request('zwave.create_new_primary');
                        self.commandRunning = false;
                        self.refresh();
                    },
                },

                {
                    text: 'Transfer Primary Role',
                    disabled: this.commandRunning,
                    click: async function() {
                        self.commandRunning = true;
                        await request('zwave.transfer_primary_role');
                        self.commandRunning = false;
                        self.refresh();
                    },
                },

                {
                    text: 'Heal Network',
                    disabled: this.commandRunning,
                    click: async function() {
                        self.commandRunning = true;
                        await request('zwave.heal');
                        self.commandRunning = false;
                        self.refresh();
                    },
                },

                {
                    text: 'Soft Reset',
                    disabled: this.commandRunning,
                    click: async function() {
                        if (!confirm('Are you sure that you want to do a device soft reset? Network information will not be lost')) {
                            return;
                        }

                        await request('zwave.soft_reset');
                    },
                },

                {
                    text: 'Hard Reset',
                    disabled: this.commandRunning,
                    click: async function() {
                        if (!confirm('Are you sure that you want to do a device soft reset? ALL network information will be lost!')) {
                            return;
                        }

                        await request('zwave.hard_reset');
                    },
                },
            ]
        },
    },

    methods: {
        refreshNodes: async function () {
            this.loading.nodes = true;
            this.loading.values = true;

            this.nodes = await request('zwave.get_nodes');
            this.loading.nodes = false;

            this.values = Object.values(this.nodes).reduce((values, node) => {
                values = {
                    ...Object.values(node.values).reduce((values, value) => {
                        values[value.value_id] = {
                            node_id: node.node_id,
                            ...value,
                        };

                        return values;
                    }, {}),
                    ...values
                };

                return values;
            }, {});

            this.loading.values = false;
        },

        refreshGroups: async function () {
            this.loading.groups = true;
            this.groups = Object.values(await request('zwave.get_groups'))
                .filter((group) => group.index)
                .reduce((groups, group) => {
                    groups[group.index] = group;
                    return groups;
                }, {});

            if (Object.keys(this.groups).length) {
                Vue.set(this.views, 'groups', true);
            }

            this.loading.groups = false;
        },

        refreshScenes: async function () {
            this.loading.scenes = true;
            this.scenes = Object.values(await request('zwave.get_scenes'))
                .filter((scene) => scene.scene_id)
                .reduce((scenes, scene) => {
                    scenes[scene.scene_id] = scene;
                    return scenes;
                }, {});

            this.loading.scenes = false;
        },

        refreshSwitches: async function () {
            this.switches = new Set(Object.values(await request('zwave.get_switches'))
                .filter((sw) => sw.id_on_network).map((sw) => sw.value_id));

            if (this.switches.size) {
                Vue.set(this.views, 'switches', true);
            }
        },

        refreshDimmers: async function () {
            this.dimmers = new Set(Object.values(await request('zwave.get_dimmers'))
                .filter((dimmer) => dimmer.id_on_network).map((dimmer) => dimmer.value_id));

            if (this.dimmers.size) {
                Vue.set(this.views, 'dimmers', true);
            }
        },

        refreshSensors: async function () {
            this.sensors = new Set(Object.values(await request('zwave.get_sensors'))
                .filter((sensor) => sensor.id_on_network).map((sensor) => sensor.value_id));

            if (this.sensors.size) {
                Vue.set(this.views, 'sensors', true);
            }
        },

        refreshBatteryLevels: async function () {
            this.batteryLevels = new Set(Object.values(await request('zwave.get_battery_levels'))
                .filter((battery) => battery.id_on_network).map((battery) => battery.value_id));

            if (this.batteryLevels.size) {
                Vue.set(this.views, 'batteryLevels', true);
            }
        },

        refreshPowerLevels: async function () {
            this.powerLevels = new Set(Object.values(await request('zwave.get_power_levels'))
                .filter((power) => power.id_on_network).map((power) => power.value_id));

            if (this.powerLevels.size) {
                Vue.set(this.views, 'powerLevels', true);
            }
        },

        refreshBulbs: async function () {
            this.bulbs = new Set(Object.values(await request('zwave.get_bulbs'))
                .filter((bulb) => bulb.id_on_network).map((bulb) => bulb.value_id));

            if (this.bulbs.size) {
                Vue.set(this.views, 'bulbs', true);
            }
        },

        refreshDoorlocks: async function () {
            this.doorlocks = new Set(Object.values(await request('zwave.get_doorlocks'))
                .filter((lock) => lock.id_on_network).map((lock) => lock.value_id));

            if (this.doorlocks.size) {
                Vue.set(this.views, 'doorlocks', true);
            }
        },

        refreshUsercodes: async function () {
            this.doorlocks = new Set(Object.values(await request('zwave.get_usercodes'))
                .filter((code) => code.id_on_network).map((code) => code.value_id));

            if (this.usercodes.size) {
                Vue.set(this.views, 'usercodes', true);
            }
        },

        refreshThermostats: async function () {
            this.thermostats = new Set(Object.values(await request('zwave.get_thermostats'))
                .filter((th) => th.id_on_network).map((th) => th.value_id));

            if (this.thermostats.size) {
                Vue.set(this.views, 'thermostats', true);
            }
        },

        refreshProtections: async function () {
            this.protections = new Set(Object.values(await request('zwave.get_protections'))
                .filter((p) => p.id_on_network).map((p) => p.value_id));

            if (this.protections.size) {
                Vue.set(this.views, 'protections', true);
            }
        },

        refreshStatus: async function() {
            this.loading.status = true;
            this.status = await request('zwave.status');
            this.loading.status = false;
        },

        refresh: function () {
            this.views = {
                nodes: true,
                scenes: true,
            };

            this.refreshNodes();
            this.refreshGroups();
            this.refreshScenes();
            this.refreshSwitches();
            this.refreshDimmers();
            this.refreshSensors();
            this.refreshBulbs();
            this.refreshDoorlocks();
            this.refreshUsercodes();
            this.refreshThermostats();
            this.refreshProtections();
            this.refreshBatteryLevels();
            this.refreshPowerLevels();
            this.refreshStatus();
        },

        onNodeUpdate: function(event) {
            Vue.set(this.nodes, event.node.node_id, event.node);
        },

        onViewChange: function(event) {
            Vue.set(this.selected, 'view', event.target.value);
        },

        onNodeClicked: function(event) {
            Vue.set(this.selected, 'nodeId', event.nodeId === this.selected.nodeId ? undefined : event.nodeId);
        },

        onGroupClicked: function(event) {
            Vue.set(this.selected, 'groupId', event.groupId === this.selected.groupId ? undefined : event.groupId);
        },

        onNetworkInfoModalOpen: function() {
            this.refreshStatus();
            this.modal.networkInfo.visible = true;
        },

        onCommandEvent: function(event) {
            if (event.error && event.error.length) {
                createNotification({
                    text: event.state_description + ': ' + event.error_description,
                    error: true,
                });
            }
        },

        openNetworkCommandsDropdown: function() {
            openDropdown(this.$refs.networkCommandsDropdown);
        },

        addNode: async function() {
            this.commandRunning = true;
            await request('zwave.add_node');
            this.commandRunning = false;
        },

        addToGroup: async function(nodeId, groupId) {
            this.commandRunning = true;
            await request('zwave.add_node_to_group', {
                node_id: nodeId,
                group_index: groupId,
            });

            this.commandRunning = false;
            this.refreshGroups();
        },

        removeNode: async function() {
            this.commandRunning = true;
            await request('zwave.remove_node');
            this.commandRunning = false;
        },
    },

    created: function() {
        const self = this;
        this.bus.$on('nodeClicked', this.onNodeClicked);
        this.bus.$on('groupClicked', this.onGroupClicked);
        this.bus.$on('openAddToGroupModal', () => {self.modal.group.visible = true});

        registerEventHandler(this.refreshGroups, 'platypush.message.event.zwave.ZwaveNodeGroupEvent');
        registerEventHandler(this.refreshScenes, 'platypush.message.event.zwave.ZwaveNodeSceneEvent');
        registerEventHandler(this.refreshNodes, 'platypush.message.event.zwave.ZwaveNodeRemovedEvent');
        registerEventHandler(this.onCommandEvent, 'platypush.message.event.zwave.ZwaveCommandEvent');

        registerEventHandler(this.refreshStatus,
            'platypush.message.event.zwave.ZwaveNetworkReadyEvent',
            'platypush.message.event.zwave.ZwaveNetworkStoppedEvent',
            'platypush.message.event.zwave.ZwaveNetworkErrorEvent',
            'platypush.message.event.zwave.ZwaveNetworkResetEvent');

        registerEventHandler(this.onNodeUpdate,
            'platypush.message.event.zwave.ZwaveNodeEvent',
            'platypush.message.event.zwave.ZwaveNodeAddedEvent',
            'platypush.message.event.zwave.ZwaveNodeRenamedEvent',
            'platypush.message.event.zwave.ZwaveNodeReadyEvent');
    },

    mounted: function() {
        this.refresh();
    },
});


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
            commandRunning: false,
            values: {
                switches: {},
                dimmers: {},
                sensors: {},
                battery_levels: {},
                power_levels: {},
                bulbs: {},
                doorlocks: {},
                usercodes: {},
                thermostats: {},
                protections: {},
            },
            selected: {
                view: 'nodes',
                nodeId: undefined,
                groupId: undefined,
                sceneId: undefined,
            },
            loading: {
                status: false,
                nodes: false,
                groups: false,
                scenes: false,
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
            this.nodes = await request('zwave.get_nodes');

            if (Object.keys(this.nodes).length) {
                Vue.set(this.views, 'values', true);
            }
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

        refreshValues: async function(type) {
            Vue.set(this.values, type, Object.values(await request('zwave.get_' + type))
                .filter((item) => item.id_on_network)
                .reduce((values, value) => {
                    values[value.id_on_network] = true;
                    return values;
                }, {}));

            if (Object.keys(this.values[type]).length) {
                Vue.set(this.views, type, true);
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
            this.refreshValues('switches');
            this.refreshValues('dimmers');
            this.refreshValues('sensors');
            this.refreshValues('bulbs');
            this.refreshValues('doorlocks');
            this.refreshValues('usercodes');
            this.refreshValues('thermostats');
            this.refreshValues('protections');
            this.refreshValues('battery_levels');
            this.refreshValues('power_levels');
            this.refreshValues('node_config');
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
        this.bus.$on('refresh', this.refresh);
        this.bus.$on('refreshNodes', this.refreshNodes);
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
            'platypush.message.event.zwave.ZwaveNodeReadyEvent',
            'platypush.message.event.zwave.ZwaveValueAddedEvent',
            'platypush.message.event.zwave.ZwaveValueChangedEvent',
            'platypush.message.event.zwave.ZwaveValueRemovedEvent',
            'platypush.message.event.zwave.ZwaveValueRefreshedEvent');
    },

    mounted: function() {
        this.refresh();
    },
});


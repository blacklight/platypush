// Will be filled by dynamically loading device scripts
const MediaPlayers = {};

Vue.component('media-devices', {
    template: '#tmpl-media-devices',
    props: {
        bus: { type: Object },
        localPlayer: { type: String },
    },

    data: function() {
        return {
            showDevicesMenu: false,
            selectedDevice: {},
            loading: false,
            devices: [],
        };
    },

    computed: {
        staticItems: function() {
            return [
                {
                    text: 'Refresh',
                    type: 'refresh',
                    icon: 'sync-alt',
                    preventClose: true,
                },
            ];
        },

        dropdownItems: function() {
            const self = this;
            const onClick = (menuItem) => {
                return () => {
                    if (self.loading) {
                        return;
                    }

                    self.selectDevice(menuItem.device);
                };
            };

            return self.staticItems.concat(
                self.devices.map($dev => {
                    return {
                        name: $dev.name,
                        text: $dev.text || $dev.name,
                        icon: $dev.icon,
                        iconClass: $dev.iconClass,
                        device: $dev,
                    };
                })
            ).map(item => {
                item.click = item.type === 'refresh' ? self.refreshDevices : onClick(item);
                item.disabled = self.loading;
                return item;
            });
        },
    },

    methods: {
        refreshDevices: async function() {
            if (this.loading) {
                return;
            }

            this.loading = true;
            const self = this;

            try {
                const promises = Object.entries(MediaPlayers).map((p) => {
                    const playerType = p[0];
                    const Player = p[1];

                    return new Promise((resolve, reject) => {
                        const player = new Player();

                        if (player.scan) {
                            player.scan().then(devs => {
                                resolve(devs.map(device => {
                                    const handler = new Player();
                                    handler.device = device;
                                    return handler;
                                }));
                            });

                            return;
                        }

                        if (player.type === 'local') {
                            player.device = {
                                plugin: self.localPlayer,
                            };
                        } else {
                            player.device = {};
                        }

                        resolve([player]);
                    });
                });

                this.devices = (await Promise.all(promises)).reduce((list, devs) => {
                    return [...list, ...devs];
                }, []).sort((a,b) => {
                    if (a.type === 'local')
                        return -1;
                    if (b.type === 'local')
                        return 1;
                    if (a.type === 'browser')
                        return -1;
                    if (b.type === 'browser')
                        return 1;
                    if (a.type !== b.type)
                        return b.type.localeCompare(a);
                    return b.name.localeCompare(a);
                });

                this.devices.forEach(dev => {
                    dev.status().then(status => {
                        self.bus.$emit('status-update', {
                            device: dev,
                            status: status,
                        });
                    });
                });
            } finally {
                this.loading = false;
                this.selectDevice(this.devices.filter(_ => _.type === 'local')[0]);
            }
        },

        selectDevice: function(device) {
            this.selectedDevice = device;
            this.bus.$emit('selected-device', device);
        },

        openDevicesMenu: function() {
            openDropdown(this.$refs.menu);
        },
    },

    created: function() {
        this.refreshDevices();
    },
});


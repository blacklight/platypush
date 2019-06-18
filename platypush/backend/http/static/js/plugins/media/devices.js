// Will be filled by dynamically loading device scripts
var mediaPlayers = {};

Vue.component('media-devices', {
    template: '#tmpl-media-devices',
    props: {
        bus: { type: Object },
        playerPlugin: { type: String },
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
                },
                {
                    name: this.playerPlugin,
                    text: this.playerPlugin,
                    type: 'local',
                    icon: 'desktop',
                },
                {
                    name: 'browser',
                    text: 'Browser',
                    type: 'browser',
                    icon: 'laptop',
                },
            ];
        },

        dropdownItems: function() {
            const items = this.staticItems.concat(
                this.devices.map(dev => {
                    return {
                        name: dev.name,
                        text: dev.name,
                        type: dev.__type__,
                        icon: dev.icon,
                        iconClass: dev.iconClass,
                        device: dev,
                    };
                })
            );

            const self = this;

            const onClick = (item) => {
                return () => {
                    if (self.loading) {
                        return;
                    }

                    self.selectDevice(item);
                };
            };

            for (var i=0; i < items.length; i++) {
                if (items[i].type === 'refresh') {
                    items[i].click = this.refreshDevices;
                } else {
                    items[i].click = onClick(items[i]);
                }

                items[i].disabled = this.loading;
            }

            return items;
        },
    },

    methods: {
        refreshDevices: async function() {
            if (this.loading) {
                return;
            }

            this.loading = true;
            var devices;

            try {
                const promises = Object.entries(mediaPlayers).map((p) => {
                    const player = p[0];
                    const handler = p[1];

                    return new Promise((resolve, reject) => {
                        handler.scan().then(devs => {
                            for (var i=0; i < devs.length; i++) {
                                devs[i].__type__ = player;

                                if (handler.icon) {
                                    devs[i].icon = handler.icon instanceof Function ? handler.icon(devs[i]) : handler.icon;
                                } else if (handler.iconClass) {
                                    devs[i].iconClass = handler.iconClass instanceof Function ? handler.iconClass(devs[i]) : handler.iconClass;
                                }
                            }

                            resolve(devs);
                        });
                    });
                });

                this.devices = (await Promise.all(promises)).reduce((list, devs) => {
                    for (const d of devs) {
                        list.push(d);
                    }

                    return list;
                }, []);
            } finally {
                this.loading = false;
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
        this.selectDevice(this.dropdownItems.filter(_ => _.type === 'local')[0]);
        this.refreshDevices();
    },
});


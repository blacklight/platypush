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
        };
    },

    computed: {
        dropdownItems: function() {
            var items = [
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

            const self = this;
            const onClick = (item) => {
                return () => {
                    self.selectDevice(item);
                };
            };

            for (var i=0; i < items.length; i++) {
                items[i].click = onClick(items[i]);
            }

            return items;
        },
    },

    methods: {
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
    },
});


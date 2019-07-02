const SwitchDevice = Vue.component('switch-device', {
    template: '#tmpl-switch-device',
    props: {
        bus: {
            type: Object,
        },

        device: {
            type: Object,
            default: () => {},
        },
    },
});

const SwitchType = Vue.component('switch-type', {
    template: '#tmpl-switch-type',
    props: {
        bus: {
            type: Object,
        },

        name: {
            type: String,
        },

        devices: {
            type: Object,
            default: () => {},
        },
    },
});

Vue.component('switches', {
    template: '#tmpl-switches',
    props: ['config'],

    data: function() {
        return {
            bus: new Vue({}),
            plugins: {},
        };
    },

    methods: {
        refresh: async function() {
            if (!this.config.plugins) {
                console.warn('Please specify a list of switch plugins in your switch section configuration');
                return;
            }

            const promises = this.config.plugins.map(plugin => {
                return new Promise((resolve, reject) => {
                    request(plugin + '.status').then(status => {
                        const ret = {};
                        ret[plugin] = status;
                        resolve(ret);
                    });
                });
            });

            const statuses = (await Promise.all(promises)).reduce((obj, status) => {
                obj[Object.keys(status)[0]] = Object.values(status)[0].reduce((obj2, device) => {
                    device.type = Object.keys(status)[0];
                    obj2[device.id] = device;
                    return obj2;
                }, {});

                return obj;
            }, {});

            for (const [name, status] of Object.entries(statuses)) {
                this.plugins[name] = status;

                const switchType = new SwitchType();
                switchType.bus = this.bus;
                switchType.name = name;
                switchType.devices = this.plugins[name];

                switchType.$mount();
                this.$refs.root.appendChild(switchType.$el);
            }
        },

        toggle: async function(type, device) {
            let status = await request(type + '.toggle', {device: device});
            this.plugins[type][status.id].on = status.on;
        },
    },

    mounted: function() {
        const self = this;
        this.refresh();

        this.bus.$on('switch-toggled', (evt) => {
            self.toggle(evt.type, evt.device);
        });
    },
});


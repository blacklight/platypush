Vue.component('sensor-metric', {
    template: '#tmpl-sensor-metric',
    props: {
        bus: {
            type: Object,
        },

        name: {
            type: String,
        },

        value: {
            type: [String, Number, Object, Boolean, Array],
        },
    },
});

Vue.component('sensors', {
    template: '#tmpl-sensors',
    props: ['config'],

    data: function() {
        return {
            bus: new Vue({}),
            metrics: {},
        };
    },

    methods: {
        refresh: async function() {
            if (!this.config.plugins) {
                console.warn('Please specify a list of sensor plugins in your sensors section configuration');
                return;
            }

            const promises = this.config.plugins.map(plugin => {
                return new Promise((resolve, reject) => {
                    if (plugin === 'serial') {
                        // Don't refresh reads over the serial port,
                        // as it might mess up any data transfer already in progress
                        resolve();
                        return;
                    }

                    request(plugin + '.get_measurement').then(metrics => {
                        resolve(metrics);
                    });
                });
            });

            Vue.set(this, 'metrics', (await Promise.all(promises)).reduce((obj, metrics) => {
                if (!metrics)
                    return obj;

                for (const [name, value] of Object.entries(metrics)) {
                    obj[name] = value;
                }

                return obj;
            }, {}));
        },

        onSensorEvent: function(event) {
            const data = event.data;
            for (const [name, value] of Object.entries(data)) {
                Vue.set(this.metrics, name, value);
            }
        },
    },

    mounted: function() {
        registerEventHandler(this.onSensorEvent, 'platypush.message.event.sensor.SensorDataChangeEvent');
        this.refresh();
    },
});


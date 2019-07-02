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
                    request(plugin + '.get_measurement').then(metrics => {
                        resolve(metrics);
                    });
                });
            });

            this.metrics = (await Promise.all(promises)).reduce((obj, metrics) => {
                for (const [name, value] of Object.entries(metrics)) {
                    obj[name] = value;
                }

                return obj;
            }, {});
        },

        onSensorEvent: function(event) {
            const data = event.data;
            this.metrics[data.name] = data.value;
        },
    },

    mounted: function() {
        registerEventHandler(this.onSensorEvent, 'platypush.message.event.sensor.SensorDataChangeEvent');
        this.refresh();
    },
});


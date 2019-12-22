Vue.component('gpio', {
    template: '#tmpl-gpio',
    props: ['config'],

    data: function() {
        return {
            pins: {},
        };
    },

    methods: {
        refresh: async function() {
            const pins = await request('gpio.read_all');
            this.pins = pins.reduce((pins, pin) => {
                pins[pin.pin] = {
                    name: pin.name,
                    number: pin.pin,
                    on: !!pin.value,
                };

                return pins;
            }, {});
        },

        toggle: async function(pin) {
            await request('gpio.write', {pin: pin, value: +(!this.pins[pin].on)});
            this.refresh();
        },
    },

    mounted: function() {
        this.refresh();
    },
});


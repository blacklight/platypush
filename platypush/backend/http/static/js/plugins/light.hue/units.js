Vue.component('light-hue-unit', {
    template: '#tmpl-light-hue-unit',
    props: ['id','capabilities','config','name',
            'uniqueid','type','productname','modelid',
            'manufacturername', 'swupdate','swversion','value',
            'collapsed'],

    methods: {
        toggled: async function(event) {
            await request(
                'light.hue.' + (event.value ? 'on' : 'off'),
                { lights: [this.id] },
            );

            this.$emit('input', {
                ...this.value,
                id: this.id,
                on: event.value
            });
        },

        colorChanged: async function(event) {
            await request(
                'light.hue.xy',
                { value: event.xy, lights: [this.id] },
            );

            this.$emit('input', {
                ...this.value,
                id: this.id,
                xy: event.xy
            });
        },

        briChanged: async function(event) {
            await request(
                'light.hue.bri',
                { value: event.bri, lights: [this.id] },
            );

            this.$emit('input', {
                ...this.value,
                id: this.id,
                bri: event.bri
            });
        },

        ctChanged: async function(event) {
            await request(
                'light.hue.ct',
                { value: event.ct, lights: [this.id] },
            );

            this.$emit('input', {
                ...this.value,
                id: this.id,
                ct: event.ct
            });
        },

        propertiesCollapsedToggled: function() {
            this.$emit('properties-collapsed-toggled', {
                type: 'unit',
                id: this.id
            });
        },
    },
});


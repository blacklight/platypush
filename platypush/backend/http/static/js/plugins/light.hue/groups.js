Vue.component('light-hue-group', {
    template: '#tmpl-light-hue-group',
    props: ['id','name'],
});

Vue.component('light-hue-group-controller', {
    template: '#tmpl-light-hue-group-controller',
    props: ['id','groups','value','collapsed'],
    computed: {
        lights: function() {
            return this.groups[this.id].lights;
        },

        name: function() {
            return this.groups[this.id].name;
        },

        properties: function() {
            var self = this;
            var avg = function(values) {
                if (values.length) {
                    return values.reduce((sum,value) => sum+value) / values.length;
                } else {
                    return 0;
                }
            };

            var getLightValues = function(attribute) {
                return Object.values(self.lights).map(
                    light => attribute in light.state && light.state.on ? light.state[attribute] : undefined
                ).filter(value => value !== undefined);
            };

            return {
                xy: [
                    avg(getLightValues('xy').map(_ => parseFloat(_[0]))),
                    avg(getLightValues('xy').map(_ => parseFloat(_[1])))
                ],
                ct: avg(getLightValues('ct')),
                bri: avg(getLightValues('bri')),
            };
        },
    },

    methods: {
        toggled: async function(event) {
            await request(
                'light.hue.' + (event.value ? 'on' : 'off'),
                { groups: [this.id] },
            );

            this.$emit('input', {
                ...this.value,
                lights: this._updateLights('on', event.value),
            });

            this.$emit('input', {...this.value, state: {...this.value.state, any_on: event.value, all_on: event.value}});
        },

        propertiesCollapsedToggled: function() {
            this.$emit('properties-collapsed-toggled', {
                type: 'group',
                id: this.id,
            });
        },

        colorChanged: async function(event) {
            await request(
                'light.hue.xy',
                { value: event.xy, groups: [this.id] },
            );

            this.$emit('input', {
                ...this.value,
                lights: this._updateLights('xy', event.xy),
            });
        },

        briChanged: async function(event) {
            await request(
                'light.hue.bri',
                { value: event.bri, groups: [this.id] },
            );

            this.$emit('input', {
                ...this.value,
                lights: this._updateLights('bri', event.bri),
            });
        },

        ctChanged: async function(event) {
            await request(
                'light.hue.ct',
                { value: event.ct, groups: [this.id] },
            );

            this.$emit('input', {
                ...this.value,
                lights: this._updateLights('ct', event.ct),
            });
        },

        _updateLights: function(attr, value) {
            var lights = [];
            for (const light of Object.values(this.value.lights)) {
                var state = light.state;
                state[attr] = value;
                lights.push({
                    ...light,
                    state: state,
                });
            }

            return lights;
        },
    },
});


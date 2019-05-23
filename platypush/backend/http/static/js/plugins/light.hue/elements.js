Vue.component('light-hue-property-selector', {
    template: '#tmpl-light-hue-property-selector',
    props: ['id','value'],
    computed: {
        rgb: function() {
            if (!(this.value && 'xy' in this.value)) {
                return;
            }

            return toRGB(this.value.xy[0], this.value.xy[1], this.value.bri);
        },
    },

    methods: {
        changed: function(event) {
            var value = parseInt(event.target.value);
            var xy;

            if (event.target.getAttribute('class').split(' ').indexOf('bri') > -1) {
                this.$emit('bri-changed', {bri: value});
                return;
            } else if (event.target.getAttribute('class').split(' ').indexOf('ct') > -1) {
                this.$emit('ct-changed', {ct: value});
                return;
            }

            if (event.target.getAttribute('class').split(' ').indexOf('red') > -1) {
                xy = toXY(value, this.rgb[1], this.rgb[2]);
            } else if (event.target.getAttribute('class').split(' ').indexOf('green') > -1) {
                xy = toXY(this.rgb[0], value, this.rgb[2]);
            } else if (event.target.getAttribute('class').split(' ').indexOf('blue') > -1) {
                xy = toXY(this.rgb[0], this.rgb[1], value);
            } else {
                return;
            }

            this.$emit('color-changed', {xy: xy});
        },
    },
});


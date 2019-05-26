Vue.component('light-hue-animation-color_transition', {
    template: '#tmpl-light-hue-animation-color_transition',
    data: function() {
        return {
            value: {
                hue_range: [0,65535],
                sat_range: [150,255],
                bri_range: [190,255],
                hue_step: 150,
                sat_step: 5,
                bri_step: 2,
                transition_seconds: 1,
                duration: undefined,
            },
        };
    },

    computed: {
        hueStepRange: function() {
            return [1, parseInt((this.value.hue_range[1]-this.value.hue_range[0])/2)-1];
        },
        satStepRange: function() {
            return [1, parseInt((this.value.sat_range[1]-this.value.sat_range[0])/2)-1];
        },
        briStepRange: function() {
            return [1, parseInt((this.value.bri_range[1]-this.value.bri_range[0])/2)-1];
        },
        transitionSecondsRange: function() {
            return [0.1, 60];
        },
        durationRange: function() {
            return [0, 600];
        },
    },

    methods: {
        hueRangeChanged: function(value) {
            this.value.hue_range = value;
        },
        satRangeChanged: function(value) {
            this.value.sat_range = value;
        },
        briRangeChanged: function(value) {
            this.value.bri_range = value;
        },
        onTransitionSecondsChange: function(event) {
            this.value.transition_seconds = event.target.value;
        },
        onDurationChanged: function(event) {
            var value = event.target.value;
            if (value == null || value.length === 0 || parseFloat(value) == 0) {
                value = undefined;
            }

            this.value.duration = value;
        },
    },
});


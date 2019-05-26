Vue.component('light-hue-animation-blink', {
    template: '#tmpl-light-hue-animation-blink',
    data: function() {
        return {
            value: {
                transition_seconds: 1,
                duration: undefined,
            },
            transitionSecondsRange: [0.1, 60],
            durationRange: [0, 600],
        };
    },

    methods: {
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


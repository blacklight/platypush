Vue.component('camera-pi', {
    template: '#tmpl-camera-pi',
    mixins: [cameraMixin],

    methods: {
        startStreaming: function() {
            this._startStreaming('pi');
        },

        capture: function() {
            this._capture('pi');
        },
    },

    mounted: function() {
        this.attrs.resolution = [640, 480];
    }
});


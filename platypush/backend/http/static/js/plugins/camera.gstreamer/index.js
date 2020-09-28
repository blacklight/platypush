Vue.component('camera-gstreamer', {
    template: '#tmpl-camera-gstreamer',
    mixins: [cameraMixin],

    methods: {
        startStreaming: function() {
            this._startStreaming('gstreamer');
        },

        capture: function() {
            this._capture('gstreamer');
        },
    },
});


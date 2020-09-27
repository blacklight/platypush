Vue.component('camera-ffmpeg', {
    template: '#tmpl-camera-ffmpeg',
    mixins: [cameraMixin],

    methods: {
        startStreaming: function() {
            this._startStreaming('ffmpeg');
        },

        capture: function() {
            this._capture('ffmpeg');
        },
    },
});


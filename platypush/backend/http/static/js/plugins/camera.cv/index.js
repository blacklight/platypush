Vue.component('camera-cv', {
    template: '#tmpl-camera-cv',
    mixins: [cameraMixin],

    methods: {
        startStreaming: function() {
            this._startStreaming('cv');
        },

        capture: function() {
            this._capture('cv');
        },
    },
});


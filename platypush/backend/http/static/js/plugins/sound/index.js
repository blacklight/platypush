Vue.component('sound', {
    template: '#tmpl-sound',
    props: ['config'],

    data: function() {
        return {
            bus: new Vue({}),
            recording: false,
        };
    },

    methods: {
        startRecording: function() {
            this.recording = true;
        },

        stopRecording: function() {
            this.recording = false;
        },
    },
});


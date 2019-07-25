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

        stopRecording: async function() {
            this.recording = false;
            await request('sound.stop_recording')
        },
    },
});


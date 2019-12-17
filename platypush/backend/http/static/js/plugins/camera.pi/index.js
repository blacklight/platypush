Vue.component('camera-pi', {
    template: '#tmpl-camera-pi',
    props: ['config'],

    data: function() {
        return {
            bus: new Vue({}),
            streaming: false,
            capturing: false,
        };
    },

    methods: {
        startStreaming: function() {
            if (this.streaming)
                return;

            this.streaming = true;
            this.capturing = false;
            this.$refs.frame.setAttribute('src', '/camera/pi/stream');
        },

        stopStreaming: function() {
            if (!this.streaming)
                return;

            this.streaming = false;
            this.capturing = false;
            this.$refs.frame.removeAttribute('src');
        },

        capture: function() {
            if (this.capturing)
                return;

            this.streaming = false;
            this.capturing = true;
            this.$refs.frame.setAttribute('src', '/camera/pi/frame?t=' + (new Date()).getTime());
        },

        onFrameLoaded: function(event) {
            if (this.capturing) {
                this.capturing = false;
            }
        },
    },

    mounted: function() {
        this.$refs.frame.addEventListener('load', this.onFrameLoaded);
    },
});


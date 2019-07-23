Vue.component('camera', {
    template: '#tmpl-camera',
    props: ['config'],

    data: function() {
        return {
            bus: new Vue({}),
            streaming: false,
            capturing: false,
        };
    },

    computed: {
        deviceId: function() {
            return this.config.device_id || 0;
        },
    },

    methods: {
        startStreaming: function() {
            if (this.streaming)
                return;

            this.streaming = true;
            this.capturing = false;
            this.$refs.frame.setAttribute('src', '/camera/' + this.deviceId + '/stream');
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
            this.$refs.frame.setAttribute('src', '/camera/' + this.deviceId + '/frame?t=' + (new Date()).getTime());
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


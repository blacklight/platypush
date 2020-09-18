var cameraMixin = {
    props: ['config'],

    data: function() {
        return {
            bus: new Vue({}),
            streaming: false,
            capturing: false,
            showParams: false,
            url: null,
            attrs: {
                resolution: this.config.resolution || [640, 480],
                device: this.config.device,
                horizontal_flip: this.config.horizontal_flip || 0,
                vertical_flip: this.config.vertical_flip || 0,
                rotate: this.config.rotate || 0,
                scale_x: this.config.scale_x || 1.0,
                scale_y: this.config.scale_y || 1.0,
                fps: this.config.fps || 16.0,
                grayscale: this.config.grayscale || 0,
                stream_format: this.config.stream_format || 'mjpeg',
            },
        };
    },

    computed: {
        params: function() {
            return {
                resolution: this.attrs.resolution,
                device: this.attrs.device != null && ('' + this.attrs.device).length > 0 ? this.attrs.device : null,
                horizontal_flip: parseInt(0 + this.attrs.horizontal_flip),
                vertical_flip: parseInt(0 + this.attrs.vertical_flip),
                rotate: parseFloat(this.attrs.rotate),
                scale_x: parseFloat(this.attrs.scale_x),
                scale_y: parseFloat(this.attrs.scale_y),
                fps: parseFloat(this.attrs.fps),
                grayscale: parseInt(0 + this.attrs.grayscale),
            };
        },

        window: function() {
            return window;
        },
    },

    methods: {
        getUrl: function(plugin, action) {
            return '/camera/' + plugin + '/' + action + '?' +
                Object.entries(this.params).filter(([k, v]) => v != null && ('' + v).length > 0)
                    .map(([k, v]) => k + '=' + v).join('&');
        },

        _startStreaming: function(plugin) {
            if (this.streaming)
                return;

            this.streaming = true;
            this.capturing = false;
            this.url = this.getUrl(plugin, 'video.' + this.attrs.stream_format);
        },

        stopStreaming: function() {
            if (!this.streaming)
                return;

            this.streaming = false;
            this.capturing = false;
            this.url = null;
        },

        _capture: function(plugin) {
            if (this.capturing)
                return;

            this.streaming = false;
            this.capturing = true;
            this.url = this.getUrl(plugin, 'photo.jpg') + '&t=' + (new Date()).getTime();
        },

        onFrameLoaded: function(event) {
            if (this.capturing) {
                this.capturing = false;
            }
        },

        onDeviceChanged: function(event) {},
        onFlipChanged: function(event) {},
        onSizeChanged: function(event) {
            const degToRad = (deg) => (deg * Math.PI)/180;
            const rot = degToRad(this.params.rotate);
            this.$refs.frameContainer.style.width = Math.round(this.params.scale_x * Math.abs(this.params.resolution[0] * Math.cos(rot) + this.params.resolution[1] * Math.sin(rot))) + 'px';
            this.$refs.frameContainer.style.height = Math.round(this.params.scale_y * Math.abs(this.params.resolution[0] * Math.sin(rot) + this.params.resolution[1] * Math.cos(rot))) + 'px';
        },

        onFpsChanged: function(event) {},
        onGrayscaleChanged: function(event) {},
    },

    mounted: function() {
        this.$refs.frame.addEventListener('load', this.onFrameLoaded);
        this.onSizeChanged();
    },
};

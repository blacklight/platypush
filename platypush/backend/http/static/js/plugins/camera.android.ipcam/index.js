Vue.component('camera-android-ipcam', {
    template: '#tmpl-camera-android-ipcam',
    props: ['config'],

    data: function() {
        return {
            bus: new Vue({}),
            loading: false,
            streaming: false,
            capturing: false,
            recording: false,
            cameras: {},
            selectedCamera: undefined,
        };
    },

    computed: {
        hasMultipleCameras: function () {
            return Object.keys(this.cameras).length > 1;
        },
    },

    methods: {
        startStreaming: function() {
            if (this.streaming)
                return;

            const cam = this.cameras[this.selectedCamera];
            this.streaming = true;
            this.capturing = false;
            this.$refs.frame.setAttribute('src', cam.stream_url);
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

            const cam = this.cameras[this.selectedCamera];
            this.streaming = false;
            this.capturing = true;
            this.$refs.frame.setAttribute('src', cam.image_url + '?t=' + (new Date()).getTime());
        },

        onFrameLoaded: function(event) {
            if (this.capturing)
                this.capturing = false;
        },

        onCameraSelected: function(event) {
            this.selectedCamera = event.target.value;
        },

        flipCamera: async function() {
            const cam = this.cameras[this.selectedCamera];
            this.loading = true;

            try {
                const value = !cam.ffc;
                await request('camera.android.ipcam.set_front_facing_camera', {
                    activate: value, camera: cam.name
                });

                this.cameras[this.selectedCamera].ffc = value;
            } finally {
                this.loading = false;
            }
        },

        updateCameraStatus: async function() {
            this.loading = true;

            try {
                const cameras = await request('camera.android.ipcam.status');
                this.cameras = cameras.reduce((cameras, cam) => {
                    for (const attr of ['stream_url', 'image_url', 'audio_url']) {
                        if (cam[attr].startsWith('https://')) {
                            cam[attr] = cam[attr].replace('https://', 'http://');
                        }

                        if (cam.name in this.config.cameras && this.config.cameras[cam.name].username) {
                            cam[attr] = 'http://' + this.config.cameras[cam.name].username + ':' +
                                this.config.cameras[cam.name].password + '@' + cam[attr].substr(7);
                        }
                    }

                    cameras[cam.name] = cam;
                    return cameras;
                }, {});

                if (cameras.length)
                    this.selectedCamera = cameras[0].name;

            } finally {
                this.loading = false;
            }
        },
    },

    mounted: function() {
        this.$refs.frame.addEventListener('load', this.onFrameLoaded);
        this.updateCameraStatus();
    },
});


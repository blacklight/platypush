Vue.component('camera-ir-mlx90640', {
    template: '#tmpl-camera-ir-mlx90640',
    props: ['config'],

    data: function() {
        return {
            bus: new Vue({}),
            capturing: false,
            rotate: this.config.rotate || 0,
            grayscale: false,
        };
    },

    methods: {
        startStreaming: async function() {
            if (this.capturing)
                return;

            this.capturing = true;

            while (this.capturing) {
                const img = await request('camera.ir.mlx90640.capture', {
                    format: 'png',
                    rotate: this.rotate,
                    grayscale: this.grayscale,
                });

                this.$refs.frame.setAttribute('src', 'data:image/png;base64,' + img);
            }
        },

        stopStreaming: async function() {
            await request('camera.ir.mlx90640.stop');
            this.capturing = false;
        },
    },
});


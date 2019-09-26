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
            this.$refs.frame.setAttribute('src', '/camera/ir/mlx90640/stream?rotate='
                + this.rotate + '&grayscale=' + (this.grayscale ? 1 : 0) + '&t='
                + (new Date()).getTime());
        },

        stopStreaming: async function() {
            await request('camera.ir.mlx90640.stop');
            this.$refs.frame.removeAttribute('src');
            this.capturing = false;
        },

        onRotationChange: function() {
            this.rotate = parseInt(this.$refs.rotate.value);
            const cameraContainer = this.$el.querySelector('.camera-container');

            switch (this.rotate) {
                case 0:
                case 180:
                    cameraContainer.style.width = '640px';
                    cameraContainer.style.minWidth = '640px';
                    cameraContainer.style.height = '480px';
                    cameraContainer.style.minHeight = '480px';
                    break;

                case 90:
                case 270:
                    cameraContainer.style.width = '480px';
                    cameraContainer.style.minWidth = '480px';
                    cameraContainer.style.height = '640px';
                    cameraContainer.style.minHeight = '640px';
                    break;
            }
        },
    },

    mounted: function() {
        this.onRotationChange();
    },
});


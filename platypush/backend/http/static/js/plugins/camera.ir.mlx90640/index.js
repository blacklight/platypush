Vue.component('camera-ir-mlx90640', {
    template: '#tmpl-camera-ir-mlx90640',
    mixins: [cameraMixin],

    methods: {
        startStreaming: function() {
            this._startStreaming('ir.mlx90640');
        },

        capture: function() {
            this._capture('ir.mlx90640');
        },
    },

    mounted: function() {
        this.attrs.resolution = [32, 24];
    }
});


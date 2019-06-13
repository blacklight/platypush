Vue.component('media-controls', {
    template: '#tmpl-media-controls',
    props: {
        bus: { type: Object },
        item: {
            type: Object,
            default: () => {},
        }
    },

    methods: {
    },
});


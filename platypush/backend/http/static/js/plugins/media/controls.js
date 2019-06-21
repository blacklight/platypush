Vue.component('media-controls', {
    template: '#tmpl-media-controls',
    props: {
        bus: { type: Object },
        status: {
            type: Object,
            default: () => {},
        },
    },

    methods: {
    },
});


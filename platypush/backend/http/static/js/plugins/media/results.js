Vue.component('media-results', {
    template: '#tmpl-media-results',
    props: {
        bus: { type: Object },
        loading: {
            type: Boolean,
            default: false,
        },
        results: {
            type: Array,
            default: () => [],
        },
    },

    methods: {
    },
});


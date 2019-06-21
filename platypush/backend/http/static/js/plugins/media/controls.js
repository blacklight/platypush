Vue.component('media-controls', {
    template: '#tmpl-media-controls',
    mixins: [mediaUtils],
    props: {
        bus: { type: Object },
        status: {
            type: Object,
            default: () => {},
        },
    },
});


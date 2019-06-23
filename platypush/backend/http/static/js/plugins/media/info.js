Vue.component('media-info', {
    template: '#tmpl-media-info',
    mixins: [mediaUtils],
    props: {
        bus: { type: Object },

        item: {
            type: Object,
            default: () => {},
        }
    },
});


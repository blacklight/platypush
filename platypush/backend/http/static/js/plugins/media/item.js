Vue.component('media-item', {
    template: '#tmpl-media-item',
    props: {
        bus: { type: Object },
        item: {
            type: Object,
            default: () => {},
        }
    },
});


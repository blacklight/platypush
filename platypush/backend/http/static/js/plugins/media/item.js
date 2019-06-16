Vue.component('media-item', {
    template: '#tmpl-media-item',
    props: {
        bus: { type: Object },

        selected: {
            type: Boolean,
            default: false,
        },

        active: {
            type: Boolean,
            default: false,
        },

        item: {
            type: Object,
            default: () => {},
        }
    },

    methods: {
        onClick: function(event) {
            this.bus.$emit('result-clicked', this.item);
        },
    },
});


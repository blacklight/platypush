Vue.component('media-search', {
    template: '#tmpl-media-search',
    props: {
        bus: { type: Object },
        supportedTypes: { type: Object },
        playerPlugin: { type: String },
    },

    data: function() {
        return {
            searching: false,
            showFilter: false,
            query: '',

            types: Object.keys(this.supportedTypes).reduce((obj, type) => {
                obj[type] = true;
                return obj;
            }, {}),
        };
    },

    methods: {
        search: async function(event) {
            const types = Object.entries(this.types).filter(t => t[1]).map(t => t[0]);
            var results = [];

            this.searching = true;
            this.bus.$emit('results-loading');

            try {
                results = await request('media.search', {
                    query: this.query,
                    types: types,
                });
            } finally {
                this.searching = false;
                this.bus.$emit('results-ready', results);
            }
        },
    },

    created: function() {
    },
});


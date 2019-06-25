Vue.component('media-search', {
    template: '#tmpl-media-search',
    props: {
        bus: { type: Object },
        supportedTypes: { type: Object },
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

            searchTypes: Object.keys(this.supportedTypes).reduce((obj, type) => {
                if (type !== 'generic' && type !== 'base')
                    obj[type] = true;
                return obj;
            }, {}),
        };
    },

    methods: {
        isUrl: function(query) {
            const match = query.match('^([^:]+)://');
            if (match) {
                let protocol = match[1];
                if (protocol === 'https')
                    protocol = 'http';

                return protocol;
            }
        },

        search: async function(event) {
            const types = Object.entries(this.searchTypes).filter(t => t[1]).map(t => t[0]);
            const protocol = this.isUrl(this.query);

            if (protocol) {
                this.bus.$emit('results-ready', [{
                    type: protocol,
                    url: this.query,
                }]);

                return;
            }

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


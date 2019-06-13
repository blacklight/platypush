Vue.component('media', {
    template: '#tmpl-media',
    props: ['config','player'],
    data: function() {
        return {
            bus: new Vue({}),
            results: [],
            currentItem: {},
            loading: {
                results: false,
            },
        };
    },

    computed: {
        types: function() {
            return {
                file: {},
                torrent: {},
                youtube: {},
            };
        },
    },

    methods: {
        refresh: async function() {
        },

        onResultsLoading: function() {
            this.loading.results = true;
        },

        onResultsReady: function(results) {
            this.loading.results = false;
            this.results = results;
        },
    },

    created: function() {
        this.refresh();

        this.bus.$on('results-loading', this.onResultsLoading);
        this.bus.$on('results-ready', this.onResultsReady);
    },
});


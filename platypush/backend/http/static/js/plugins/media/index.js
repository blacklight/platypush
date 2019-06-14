// Will be filled by dynamically loading handler scripts
var mediaHandlers = {};

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
            return mediaHandlers;
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

            for (var i=0; i < results.length; i++) {
                results[i].handler = {};

                for (const hndl of Object.values(mediaHandlers)) {
                    if (hndl.matchesUrl(results[i].url)) {
                        results[i].handler = hndl;
                    }
                }
            }

            this.results = results;
        },
    },

    created: function() {
        this.refresh();

        this.bus.$on('results-loading', this.onResultsLoading);
        this.bus.$on('results-ready', this.onResultsReady);
    },
});


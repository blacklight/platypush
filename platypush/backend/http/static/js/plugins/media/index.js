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
            selectedDevice: undefined,
            loading: {
                results: false,
                media: false,
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
                results[i].handler = mediaHandlers[results[i].type];
            }

            this.results = results;
        },

        play: async function(item) {
        },

        info: function(item) {
            // TODO
            console.log(item);
        },

        selectDevice: function(device) {
            this.selectedDevice = device;
        },
    },

    created: function() {
        this.refresh();

        this.bus.$on('play', this.play);
        this.bus.$on('info', this.info);
        this.bus.$on('selected-device', this.selectDevice);
        this.bus.$on('results-loading', this.onResultsLoading);
        this.bus.$on('results-ready', this.onResultsReady);
    },
});


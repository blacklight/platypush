MediaPlayers.browser = Vue.extend({
    props: {
        type: {
            type: String,
            default: 'browser',
        },

        accepts: {
            type: Object,
            default: () => {
                return {
                    youtube: true,
                };
            },
        },

        name: {
            type: String,
            default: 'Browser',
        },

        iconClass: {
            type: String,
            default: 'fa fa-browser',
        },
    },

    methods: {
        status: async function() {
            return {};
        },

        play: async function(item) {
        },

        stop: async function() {
        },
    },
});


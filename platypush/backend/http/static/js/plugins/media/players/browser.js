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
                    generic: true,
                };
            },
        },

        subFormats: {
            type: Array,
            default: () => {
                return ['vtt'];
            },
        },

        name: {
            type: String,
            default: 'Browser',
        },

        iconClass: {
            type: String,
            default: 'fa fa-laptop',
        },
    },

    methods: {
        status: async function() {
            return {};
        },

        play: async function(item, subtitles) {
            let url = item.url;

            if (item.source && !item.source.match('https?://')) {
                // Non-HTTP resource streamed over HTTP
                const hostRegex = /^(https?:\/\/[^:/]+(:[0-9]+)?\/?)/;
                const baseURL = window.location.href.match(hostRegex)[1];
                url = url.replace(hostRegex, baseURL) + '?webplayer';
            }

            window.open(url, '_blank');
            return {};
        },
    },
});


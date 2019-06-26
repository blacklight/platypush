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
            if (item.source && item.source.startsWith('file://'))
                url += '?webplayer'

            let playerWindow = window.open(url, '_blank');
            console.log(playerWindow);
            return {};
        },

        stop: async function() {
        },
    },
});


MediaPlayers.kodi = Vue.extend({
    props: {
        type: {
            type: String,
            default: 'kodi',
        },

        device: {
            type: Object,
            default: () => {
                return {
                    url: undefined,
                };
            },
        },

        accepts: {
            type: Object,
            default: () => {
                return {
                    youtube: true,
                };
            },
        },

        iconClass: {
            type: String,
            default: 'fa fa-film',
        },
    },

    computed: {
        host: function() {
            if (!this.device.url) {
                return;
            }

            return this.device.url.match(/^https?:\/\/([^:]+):(\d+).*$/)[1];
        },

        name: function() {
            return this.host;
        },

        port: function() {
            if (!this.device.url) {
                return;
            }

            return parseInt(this.device.url.match(/^https?:\/\/([^:]+):(\d+).*$/)[2]);
        },

        text: function() {
            return 'Kodi '.concat('[', this.host, ']');
        },
    },

    methods: {
        scan: async function() {
            if (!('media.kodi' in __plugins__)) {
                return [];
            }

            return [
                { url: __plugins__['media.kodi'].url }
            ];
        },

        status: async function() {
            return {};
        },

        play: async function(item) {
        },

        stop: async function() {
        },
    },
});


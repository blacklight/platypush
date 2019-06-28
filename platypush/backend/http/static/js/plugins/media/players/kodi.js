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
                    host: undefined,
                };
            },
        },

        accepts: {
            type: Object,
            default: () => {
                return {
                    file: true,
                    generic: true,
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
        name: function() {
            return this.device.host;
        },

        text: function() {
            return 'Kodi '.concat('[', this.device.host, ']');
        },
    },

    methods: {
        scan: async function() {
            const plugin = __plugins__['media.kodi'];
            if (!plugin) {
                return [];
            }

            return [{ host: plugin.host }];
        },

        status: async function() {
            return await request('media.kodi.status');
        },

        play: async function(item) {
            return await request('media.kodi.play', {
                resource: item.url,
                subtitles: item.subtitles_url,
            });
        },

        pause: async function() {
            return await request('media.kodi.pause');
        },

        stop: async function() {
            return await request('media.kodi.stop');
        },

        seek: async function(position) {
            return await request('media.kodi.set_position', {
                position: position,
            });
        },

        setVolume: async function(volume) {
            return await request('media.kodi.set_volume', {
                volume: volume,
            });
        },
    },
});


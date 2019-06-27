MediaPlayers.chromecast = Vue.extend({
    props: {
        type: {
            type: String,
            default: 'chromecast',
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

        device: {
            type: null,
            address: null,
            port: null,
            uuid: null,
            status: {},
            name: '',
            model_name: null,
        },
    },

    computed: {
        name: function() {
            return this.device.name;
        },

        iconClass: function() {
            return this.device.type === 'audio' ? 'fa fa-volume-up' : 'fab fa-chromecast';
        },
    },

    methods: {
        scan: async function() {
            return await request('media.chromecast.get_chromecasts');
        },

        status: async function(device) {
            return await request('media.chromecast.status', {chromecast: device || this.device.name});
        },

        play: async function(item) {
            return await request('media.chromecast.play', {
                resource: item.url,
                chromecast: this.device.name,
                title: item.title || item.url,
                subtitles: item.subtitles_url,
                content_type: item.mime_type,
            });
        },

        pause: async function() {
            return await request('media.chromecast.pause', {chromecast: this.device.name});
        },

        stop: async function() {
            return await request('media.chromecast.stop', {chromecast: this.device.name});
        },

        seek: async function(position) {
            return await request('media.chromecast.set_position', {
                position: position,
                chromecast: this.device.name,
            });
        },

        setVolume: async function(volume) {
            return await request('media.chromecast.set_volume', {
                volume: volume,
                chromecast: this.device.name,
            });
        },
    },
});


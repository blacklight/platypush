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

        status: async function() {
            return {};
        },

        play: async function(item) {
        },

        stop: async function() {
        },
    },
});


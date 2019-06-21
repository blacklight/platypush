MediaPlayers.local = Vue.extend({
    props: {
        type: {
            type: String,
            default: 'local',
        },

        accepts: {
            type: Object,
            default: () => {
                return {
                    file: true,
                    youtube: true,
                };
            },
        },

        device: {
            type: Object,
            default: () => {
                return {
                    plugin: undefined,
                };
            },
        },

        iconClass: {
            type: String,
            default: 'fa fa-desktop',
        },
    },

    computed: {
        name: function() {
            return this.device.plugin;
        },

        pluginPrefix: function() {
            return 'media.' + this.device.plugin;
        },
    },

    methods: {
        status: async function() {
            return await request(this.pluginPrefix.concat('.status'));
        },

        play: async function(resource) {
            return await request(
                this.pluginPrefix.concat('.play'),
                {resource: resource}
            );
        },

        pause: async function() {
            return await request(this.pluginPrefix.concat('.pause'));
        },

        stop: async function() {
            return await request(this.pluginPrefix.concat('.stop'));
        },

        seek: async function(position) {
            return await request(
                this.pluginPrefix.concat('.seek'),
                {position: position},
            );
        },

        setVolume: async function(volume) {
            return await request(
                this.pluginPrefix.concat('.set_volume'),
                {volume: volume}
            );
        },
    },
});


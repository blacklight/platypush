MediaHandlers.torrent = Vue.extend({
    props: {
        bus: { type: Object },
        iconClass: {
            type: String,
            default: 'fa fa-magnet',
        },
    },

    computed: {
        dropdownItems: function() {
            return [
                {
                    text: 'Play',
                    icon: 'play',
                    action: this.play,
                },

                {
                    text: 'Download',
                    icon: 'download',
                    action: this.download,
                },

                {
                    text: 'View info',
                    icon: 'info',
                    action: this.info,
                },
            ];
        },
    },

    methods: {
        matchesUrl: function(url) {
            return !!(
                url.match('^magnet:?') ||
                url.match('^https?://.*\.torrent$') ||
                url.match('^(file://)?/.*\.torrent$')
            );
        },

        getMetadata: function(url) {
            // TODO
            return {};
        },

        play: function(item) {
        },

        download: function(item) {
        },

        info: function(item) {
        },
    },
});


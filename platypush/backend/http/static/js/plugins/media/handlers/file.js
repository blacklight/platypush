MediaHandlers.file = Vue.extend({
    props: {
        bus: { type: Object },
        iconClass: {
            type: String,
            default: 'fa fa-hdd',
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
                    text: 'Play with subtitles',
                    iconClass: 'fas fa-closed-captioning',
                    action: this.searchSubtiles,
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
        play: function(item) {
            this.bus.$emit('play', item);
        },

        download: function(item) {
        },

        info: function(item) {
        },

        searchSubtitles: function(item) {
        },
    },
});


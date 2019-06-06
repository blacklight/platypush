Vue.component('music-mpd-playlist-item', {
    template: '#tmpl-music-mpd-playlist-item',
    mixins: [utils],
    props: {
        track: {
            type: Object,
            default: {},
        },

        selected: {
            type: Boolean,
            default: false,
        },

        active: {
            type: Boolean,
            default: false,
        },

        move: {
            type: Boolean,
            default: false,
        },
    },
});


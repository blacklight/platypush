Vue.component('music-mpd-browser-item', {
    template: '#tmpl-music-mpd-browser-item',
    props: {
        id: { type: String, },
        type: { type: String, },
        name: { type: String, },
        file: { type: String, },
        time: { type: String, },
        artist: { type: String, },
        title: { type: String, },
        date: { type: String, },
        track: { type: String, },
        genre: { type: String, },
        lastModified: { type: String, },
        albumUri: { type: String, },

        selected: {
            type: Boolean,
            default: false,
        },
    },

    methods: {
    },
});


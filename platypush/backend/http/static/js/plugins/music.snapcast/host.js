Vue.component('music-snapcast-host', {
    template: '#tmpl-music-snapcast-host',
    props: {
        groups: { type: Object },
        server: { type: Object },
        streams: { type: Object },
        bus: { type: Object },
    },

    data: function() {
        return {
            collapsed: false,
        };
    },
});

Vue.component('music-snapcast-host-info', {
    props: {
        info: { type: Object }
    },
});


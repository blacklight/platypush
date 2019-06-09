Vue.component('music-snapcast-group', {
    template: '#tmpl-music-snapcast-group',
    props: {
        id: { type: String },
        clients: { type: Object },
        muted: { type: Boolean },
        name: { type: String },
        stream: { type: Object },
        server: { type: Object },
        bus: { type: Object },
    },

    methods: {
        muteToggled: function(event) {
            this.bus.$emit('group-mute-changed', {
                id: this.id,
                server: this.server,
                value: !event.value,
            });
        },
    },
});

Vue.component('music-snapcast-group-info', {
    props: ['info'],
});


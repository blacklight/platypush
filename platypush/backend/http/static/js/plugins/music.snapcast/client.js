Vue.component('music-snapcast-client', {
    template: '#tmpl-music-snapcast-client',
    props: {
        config: { type: Object },
        connected: { type: Boolean },
        host: { type: Object },
        id: { type: String },
        groupId: { type: String },
        lastSeen: { type: Object },
        snapclient: { type: Object },
        server: { type: Object },
        bus: { type: Object },
    },

    methods: {
        muteToggled: function(event) {
            this.bus.$emit('client-mute-changed', {
                id: this.id,
                server: this.server,
                value: !event.value,
            });
        },

        volumeChanged: function(event) {
            this.bus.$emit('client-volume-changed', {
                id: this.id,
                server: this.server,
                value: parseInt(event.target.value),
            });
        },
    },
});

Vue.component('music-snapcast-client-info', {
    props: ['info'],
});


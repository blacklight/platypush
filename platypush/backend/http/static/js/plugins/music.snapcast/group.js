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
    props: {
        info: { type: Object }
    },

    data: function() {
        return {
            loading: false,
        };
    },

    methods: {
        onClientUpdate: async function(event) {
            var clients = this.$refs.groupClients
                .map(row => row.querySelector('input[type=checkbox]:checked'))
                .filter(_ => _ != null)
                .map(input => input.value);

            this.loading = true;
            await request('music.snapcast.group_set_clients', {
                clients: clients,
                group: this.info.group.id,
                host: this.info.server.host.name,
                port: this.info.server.host.port,
            });

            this.loading = false;
            createNotification({
                text: 'Snapcast group successfully updated',
                image: {
                    icon: 'check',
                }
            });
        },

        onStreamUpdate: async function(event) {
            this.loading = true;
            await request('music.snapcast.group_set_stream', {
                stream_id: event.target.value,
                group: this.info.group.id,
                host: this.info.server.host.name,
                port: this.info.server.host.port,
            });

            this.loading = false;
            this.info.group.stream_id = event.target.value;

            createNotification({
                text: 'Snapcast stream successfully updated',
                image: {
                    icon: 'check',
                }
            });
        },
    },
});


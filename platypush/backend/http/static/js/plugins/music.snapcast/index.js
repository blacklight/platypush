Vue.component('music-snapcast', {
    template: '#tmpl-music-snapcast',
    props: ['config'],
    data: function() {
        return {
            hosts: {},
            ports: {},
            modal: {
                host: {
                    visible: false,
                    info: {},
                },
                group: {
                    visible: false,
                    info: {},
                },
                client: {
                    visible: false,
                    info: {},
                },
            },

            bus: new Vue({}),
        };
    },

    methods: {
        _parseServerStatus: function(status) {
            status.server.host.port = this.ports[status.server.host.name];
            var groups = {};

            for (const group of status.groups) {
                var clients = {};
                for (const client of group.clients) {
                    clients[client.id] = client;
                }

                group.clients = clients;
                groups[group.id] = group;
            }

            status.groups = groups;
            var streams = {};

            for (const stream of status.streams) {
                streams[stream.id] = stream;
            }

            status.streams = streams;
            Vue.set(this.hosts, status.server.host.name, status);
        },

        refresh: async function() {
            let hosts = await request('music.snapcast.get_backend_hosts');
            let promises = Object.keys(hosts).map(
                (host) => request('music.snapcast.status', {host: host, port: hosts[host]})
            );

            let statuses = await Promise.all(promises);
            this.hosts = {};

            for (const status of statuses) {
                this.ports[status.server.host.name] = hosts[status.server.host.name];
                this._parseServerStatus(status);
            }
        },

        onClientUpdate: function(event) {
            for (const groupId of Object.keys(this.hosts[event.host].groups)) {
                if (event.client.id in this.hosts[event.host].groups[groupId].clients) {
                    this.hosts[event.host].groups[groupId].clients[event.client.id] = event.client;
                }
            }
        },

        onGroupStreamChange: function(event) {
            this.hosts[event.host].groups[event.group].stream_id = event.stream;
        },

        onServerUpdate: function(event) {
            this._parseServerStatus(event.server);
        },

        onStreamUpdate: function(event) {
            this.hosts[event.host].streams[event.stream.id] = event.stream;
        },

        onClientVolumeChange: function(event) {
            for (const groupId of Object.keys(this.hosts[event.host].groups)) {
                if (event.client in this.hosts[event.host].groups[groupId].clients) {
                    if (event.volume != null) {
                        this.hosts[event.host].groups[groupId].clients[event.client].config.volume.percent = event.volume;
                    }

                    if (event.muted != null) {
                        this.hosts[event.host].groups[groupId].clients[event.client].config.volume.muted = event.muted;
                    }
                }
            }
        },

        onGroupMuteChange: function(event) {
            this.hosts[event.host].groups[event.group].muted = event.muted;
        },

        modalShow: function(event) {
            switch(event.type) {
                case 'host':
                    this.modal[event.type].info = this.hosts[event.host];
                    break;
                case 'group':
                    this.modal[event.type].info.server = this.hosts[event.host].server;
                    this.modal[event.type].info.group = this.hosts[event.host].groups[event.group];
                    this.modal[event.type].info.streams = this.hosts[event.host].streams;
                    this.modal[event.type].info.clients = {};

                    for (const group of Object.values(this.hosts[event.host].groups)) {
                        for (const client of Object.values(group.clients)) {
                            this.modal[event.type].info.clients[client.id] = client;
                        }
                    }

                    break;
                case 'client':
                    this.modal[event.type].info = this.hosts[event.host].groups[event.group].clients[event.client];
                    this.modal[event.type].info.server = this.hosts[event.host].server;
                    break;
            }

            this.modal[event.type].visible = true;
        },

        groupMute: async function(event) {
            await request('music.snapcast.mute', {
                group: event.id,
                host: event.server.ip || event.server.name,
                port: event.server.port,
                mute: event.value,
            });

            this.hosts[event.server.name].groups[event.id].muted = event.value;
        },

        clientMute: async function(event) {
            await request('music.snapcast.mute', {
                client: event.id,
                host: event.server.ip || event.server.name,
                port: event.server.port,
                mute: event.value,
            });

            for (const groupId of Object.keys(this.hosts[event.server.name].groups)) {
                if (event.id in this.hosts[event.server.name].groups[groupId].clients) {
                    this.hosts[event.server.name].groups[groupId].clients[event.id].config.volume.muted = event.value;
                }
            }
        },

        clientSetVolume: async function(event) {
            await request('music.snapcast.volume', {
                client: event.id,
                host: event.server.ip || event.server.name,
                port: event.server.port,
                volume: event.value,
            });

            for (const groupId of Object.keys(this.hosts[event.server.name].groups)) {
                if (event.id in this.hosts[event.server.name].groups[groupId].clients) {
                    this.hosts[event.server.name].groups[groupId].clients[event.id].config.volume.percent = event.value;
                }
            }
        },
    },

    created: function() {
        this.refresh();

        registerEventHandler(this.onClientUpdate,
            'platypush.message.event.music.snapcast.ClientConnectedEvent',
            'platypush.message.event.music.snapcast.ClientDisconnectedEvent',
            'platypush.message.event.music.snapcast.ClientNameChangeEvent');

        registerEventHandler(this.onGroupStreamChange, 'platypush.message.event.music.snapcast.GroupStreamChangeEvent');
        registerEventHandler(this.onServerUpdate, 'platypush.message.event.music.snapcast.ServerUpdateEvent');
        registerEventHandler(this.onStreamUpdate, 'platypush.message.event.music.snapcast.StreamUpdateEvent');
        registerEventHandler(this.onClientVolumeChange, 'platypush.message.event.music.snapcast.ClientVolumeChangeEvent');
        registerEventHandler(this.onGroupMuteChange, 'platypush.message.event.music.snapcast.GroupMuteChangeEvent');

        this.bus.$on('group-mute-changed', this.groupMute);
        this.bus.$on('client-mute-changed', this.clientMute);
        this.bus.$on('client-volume-changed', this.clientSetVolume);
        this.bus.$on('modal-show', this.modalShow);
    },
});


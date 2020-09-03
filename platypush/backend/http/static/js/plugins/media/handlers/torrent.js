MediaHandlers.torrent = MediaHandlers.base.extend({
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
                    text: 'Download (on server)',
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

    data: function() {
        return {
            torrentStatus: {},
        };
    },

    methods: {
        matchesUrl: function(url) {
            return !!(
                url.match('^magnet:?') ||
                url.match('^https?://.*\.torrent$') ||
                url.match('^(file://)?/.*\.torrent$')
            );
        },

        getTorrentPlugin: async function() {
            if (this.config && this.config.torrent_plugin) {
                return this.config.torrent_plugin;
            }

            const config = await request('inspect.get_config');
            if ('rtorrent' in config)
                return 'rtorrent';
            if ('webtorrent' in config)
                return 'webtorrent';
            return 'torrent'
        },

        getMetadata: async function(item, onlyBase=false) {
            let status = {};

            if (!onlyBase)
                status = await this.status({url: item.url});

            let transferInfo = {};
            if (item.url in this.torrentStatus)
                transferInfo = this.torrentStatus[item.url];

            return {...status, ...transferInfo};
        },

        play: async function(item) {
            let status = await this.download(item);
            status.waitingPlay = true;
            const torrentId = this.getTorrentUrlOrHash(item.url);

            if (torrentId in this.torrentStatus) {
                this.firePlay(event);
            }
        },

        pause: async function(item) {
            const torrentPlugin = await this.getTorrentPlugin();
            const torrentId = this.getTorrentUrlOrHash(item.url);
            let status = {};

            if (item.paused) {
                status = await request(torrentPlugin + '.resume', {torrent: torrentId});
            } else {
                status = await request(torrentPlugin + '.pause', {torrent: torrentId});
            }

            this.mergeStatus(status);
        },

        remove: async function(item) {
            const torrentPlugin = await this.getTorrentPlugin();
            const torrentId = this.getTorrentUrlOrHash(item.url);
            let status = await request(torrentPlugin + '.remove', {torrent: torrentId});
            if (torrentId in this.torrentStatus)
                delete this.torrentStatus[torrentId];
        },

        status: async function(item) {
            const torrentPlugin = await this.getTorrentPlugin();
            if (item) {
                const torrentId = this.getTorrentUrlOrHash(typeof item === 'string' ? item : item.url);
                return await request(torrentPlugin + '.status', {
                    torrent: torrentId,
                });
            }

            return await request(torrentPlugin + '.status');
        },

        getTorrentUrlOrHash: function(torrent) {
            if (torrent.startsWith('magnet:?')) {
                m = torrent.match(/xt=urn:btih:([^&/]+)/, torrent)
                if (m) {
                    return m[1];  // Torrent hash
                }
            }

            return torrent;
        },

        download: async function(item) {
            const torrentPlugin = await this.getTorrentPlugin();
            let status = await this.status(item.url);

            if (status && Object.keys(status).length > 1) {
                createNotification({
                    text: 'This torrent is already being downloaded, please play the downloading local media file instead',
                    image: {
                        icon: 'download',
                    },
                });

                return status;
            }

            status = await request(
                torrentPlugin + '.download',
                {
                    torrent: item.url,
                    _async: true,
                    is_media: true,
                },
                timeout=120000  // Wait up to two minutes while downloading enough torrent chunks
            );

            const torrentId = this.getTorrentUrlOrHash(item.url);
            this.torrentStatus[torrentId] = {
                ...item, ...status,
                scheduledPlay: false,
                torrentState: status.state,
                state: 'idle',
            };

            return this.torrentStatus[torrentId];
        },

        onTorrentEvent: function(event) {
            this.mergeStatus(event);
        },

        onTorrentQueued: function(event) {
            if (!this.mergeStatus(event))
                this.torrentStatus[event.url] = event;

            createNotification({
                text: 'Torrent download queued. Will start playing when enough chunks have been downloaded',
                image: {
                    icon: 'clock',
                },
            });
        },

        onTorrentStart: function(event) {
            if (!this.mergeStatus(event))
                return;

            createNotification({
                text: 'Download of '.concat(event.name, ' started'),
                image: {
                    icon: 'download',
                },
            });
        },

        onTorrentStop: function(event) {
            if (!this.mergeStatus(event))
                return;

            const torrentId = this.getTorrentUrlOrHash(event.url);
            if (torrentId in this.torrentStatus)
                delete this.torrentStatus[torrentId];

            this.bus.$emit('torrent-status-update', this.torrentStatus);
        },

        onTorrentProgress: function(event) {
            if (!this.mergeStatus(event))
                return;

            const torrentId = this.getTorrentUrlOrHash(event.url);
            if (this.torrentStatus[torrentId].waitingPlay)
                this.firePlay(event);
        },

        onTorrentCompleted: function(event) {
            if (!this.mergeStatus(event))
                return;

            const torrentId = this.getTorrentUrlOrHash(event.url);
            if (torrentId in this.torrentStatus)
                delete this.torrentStatus[event.url];

            this.bus.$emit('torrent-status-update', this.torrentStatus);

            createNotification({
                text: 'Download of '.concat(event.name, ' completed'),
                image: {
                    icon: 'check',
                },
            });
        },

        firePlay: function(item) {
            if (!item.files || !item.files.length) {
                console.warn('Torrent ' + item.url + ' has no media files available yet');
                return;
            }

            if (event.progress < 5) {
                console.warn('Please wait for enough chunks to be downloaded before playing');
                return;
            }

            const url = 'file://' + item.files[0];
            this.bus.$emit('play', {...item, type: 'file', url: url});

            if (this.torrentStatus[item.url].waitingPlay)
                this.torrentStatus[item.url].waitingPlay = false;

            createNotification({
                text: 'Playback of '.concat(item.name, ' started'),
                image: {
                    icon: 'play',
                },
            });
        },

        mergeStatus: function(event) {
            const torrentId = this.getTorrentUrlOrHash(event.url);
            const torrentState = event.state;
            delete event.state;

            this.torrentStatus[torrentId] = {
                ...this.torrentStatus[torrentId],
                ...event,
                torrentState: torrentState,
            };

            this.bus.$emit('torrent-status-update', this.torrentStatus);
            return this.torrentStatus[torrentId];
        },
    },

    created: function() {
        registerEventHandler(this.onTorrentStart, 'platypush.message.event.torrent.TorrentDownloadStartEvent');
        registerEventHandler(this.onTorrentProgress, 'platypush.message.event.torrent.TorrentDownloadProgressEvent');
        registerEventHandler(this.onTorrentCompleted, 'platypush.message.event.torrent.TorrentDownloadCompletedEvent');
        registerEventHandler(this.onTorrentQueued, 'platypush.message.event.torrent.TorrentQueuedEvent');
        registerEventHandler(this.onTorrentStop, 'platypush.message.event.torrent.TorrentDownloadStopEvent',
            'platypush.message.event.torrent.TorrentRemovedEvent');
        registerEventHandler(this.onTorrentEvent, 'platypush.message.event.torrent.TorrentPausedEvent',
            'platypush.message.event.torrent.TorrentResumedEvent',
            'platypush.message.event.torrent.TorrentDownloadStartEvent',
            'platypush.message.event.torrent.TorrentStateChangeEvent');

        const self = this;
        this.status().then((status) => {
            if (!status)
                return;

            for (const [url, torrent] of Object.entries(status)) {
                if (!torrent.url)
                    continue;
                self.mergeStatus(torrent);
            }
        });

        setTimeout(() => {
            self.bus.$on('torrent-play', self.firePlay);
            self.bus.$on('torrent-pause', self.pause);
            self.bus.$on('torrent-remove', self.remove);
        }, 100);
    },
});


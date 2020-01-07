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

            if (item.url in this.torrentStatus) {
                this.firePlay(event);
            }
        },

        pause: async function(item) {
            let status = await request('torrent.pause', {torrent: item.torrent});
            this.mergeStatus(status);
        },

        remove: async function(item) {
            let status = await request('torrent.remove', {torrent: item.torrent});
            this.mergeStatus(status);
        },

        status: async function(item) {
            if (item) {
                return await request('torrent.status', {
                    torrent: item.url,
                });
            }

            return await request('torrent.status');
        },

        download: async function(item) {
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
                'torrent.download',
                {
                    torrent: item.url,
                    _async: true,
                    is_media: true,
                },
                timeout=120000  // Wait up to two minutes while downloading enough torrent chunks
            );

            this.torrentStatus[item.url] = {
                ...item, ...status,
                scheduledPlay: false,
                torrentState: status.state,
                state: 'idle',
            };

            return this.torrentStatus[item.url];
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

            delete this.torrentStatus[event.url];
            this.bus.$emit('torrent-status-update', this.torrentStatus);
        },

        onTorrentProgress: function(event) {
            if (!this.mergeStatus(event))
                return;

            if (this.torrentStatus[event.url].waitingPlay)
                this.firePlay(event);
        },

        onTorrentCompleted: function(event) {
            if (!this.mergeStatus(event))
                return;

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
            const torrentState = event.state;
            delete event.state;

            this.torrentStatus[event.url] = {
                ...this.torrentStatus[event.url],
                ...event,
                torrentState: torrentState,
            };

            this.bus.$emit('torrent-status-update', this.torrentStatus);
            return this.torrentStatus[event.url];
        },
    },

    created: function() {
        registerEventHandler(this.onTorrentStart, 'platypush.message.event.torrent.TorrentDownloadStartEvent');
        registerEventHandler(this.onTorrentStop, 'platypush.message.event.torrent.TorrentDownloadStopEvent');
        registerEventHandler(this.onTorrentProgress, 'platypush.message.event.torrent.TorrentDownloadProgressEvent');
        registerEventHandler(this.onTorrentCompleted, 'platypush.message.event.torrent.TorrentDownloadCompletedEvent');
        registerEventHandler(this.onTorrentQueued, 'platypush.message.event.torrent.TorrentQueuedEvent');
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


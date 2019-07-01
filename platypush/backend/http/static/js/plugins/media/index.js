// Will be filled by dynamically loading media type handler scripts
const MediaHandlers = {};

const mediaUtils = {
    methods: {
        convertTime: function(time) {
            time = parseFloat(time);   // Normalize strings
            var t = {};
            t.h = '' + parseInt(time/3600);
            t.m = '' + parseInt(time/60 - t.h*60);
            t.s = '' + parseInt(time - (t.h*3600 + t.m*60));

            for (var attr of ['m','s']) {
                if (parseInt(t[attr]) < 10) {
                    t[attr] = '0' + t[attr];
                }
            }

            var ret = [];
            if (parseInt(t.h)) {
                ret.push(t.h);
            }

            ret.push(t.m, t.s);
            return ret.join(':');
        },

        convertSize: function(size) {
            size = parseInt(size);   // Normalize strings

            const units = ['B', 'KB', 'MB', 'GB'];
            let s=size, i=0;

            for (; s > 1024 && i < units.length; i++, s = parseInt(s/1024));
            return (size / Math.pow(2, 10*i)).toFixed(2) + ' ' + units[i];
        },
    },
};

Vue.component('media', {
    template: '#tmpl-media',
    props: ['config','player'],
    mixins: [mediaUtils],

    data: function() {
        return {
            bus: new Vue({}),
            results: [],
            status: {},
            selectedDevice: {},
            deviceHandlers: {},

            loading: {
                results: false,
                media: false,
            },

            infoModal: {
                visible: false,
                loading: false,
                item: {},
            },

            torrentModal: {
                visible: false,
                items: {},
            },

            subsModal: {
                visible: false,
            },
        };
    },

    computed: {
        types: function() {
            return MediaHandlers;
        },

        torrentsDownloading: function() {
            return Object.entries(this.torrentModal.items).length > 0;
        },
    },

    methods: {
        onResultsLoading: function() {
            this.loading.results = true;
        },

        onResultsReady: async function(results) {
            for (const result of results) {
                if (result.type && MediaHandlers[result.type]) {
                    result.handler = MediaHandlers[result.type];
                } else {
                    result.type = 'generic';
                    result.handler = MediaHandlers.generic;

                    for (const [handlerType, handler] of Object.entries(MediaHandlers)) {
                        if (handler.matchesUrl && handler.matchesUrl(result.url)) {
                            result.type = handlerType;
                            result.handler = handler;
                            break;
                        }
                    }
                }

                Object.entries(await result.handler.getMetadata(result, onlyBase=true)).forEach(entry => {
                    Vue.set(result, entry[0], entry[1]);
                });
            }

            this.results = results;
            this.loading.results = false;
        },

        play: async function(item) {
            if (!this.selectedDevice.accepts[item.type]) {
                item = await this.startStreaming(item);
            }

            let status = await this.selectedDevice.play(item, item.subtitles);

            if (item.title)
                status.title = item.title;

            this.subsModal.visible = false;
            this.onStatusUpdate({
                device: this.selectedDevice,
                status: status,
            });
        },

        pause: async function() {
            let status = await this.selectedDevice.pause();
            this.onStatusUpdate({
                device: this.selectedDevice,
                status: status,
            });
        },

        stop: async function() {
            let status = await this.selectedDevice.stop();
            this.onStatusUpdate({
                device: this.selectedDevice,
                status: status,
            });
        },

        seek: async function(position) {
            let status = await this.selectedDevice.seek(position);
            this.onStatusUpdate({
                device: this.selectedDevice,
                status: status,
            });
        },

        setVolume: async function(volume) {
            let status = await this.selectedDevice.setVolume(volume);
            this.onStatusUpdate({
                device: this.selectedDevice,
                status: status,
            });
        },

        info: function(item) {
            Vue.set(this.infoModal, 'item', item);
            this.infoModal.loading = false;
            this.infoModal.visible = true;
        },

        infoLoading: function() {
            this.infoModal.loading = true;
            this.infoModal.visible = true;
        },

        startStreaming: async function(item) {
            if (typeof item === 'string')
                item = {url: item};

            const ret = await request('media.start_streaming', {
                media: item.url,
                subtitles: item.subtitles,
            });

            this.bus.$emit('streaming-started', {
                url: ret.url,
                resource: item.url,
                subtitles_url: ret.subtiles_url,
            });

            return {...item, ...ret};
        },

        searchSubs: function(item) {
            if (typeof item === 'string')
                item = {url: item};

            this.subsModal.visible = true;
            this.$refs.subs.search(item);
        },

        selectDevice: async function(device) {
            this.selectedDevice = device;
            let status = await this.selectedDevice.status();

            this.onStatusUpdate({
                device: this.selectedDevice,
                status: status,
            });
        },

        syncPosition: function(status) {
            if (!status)
                return;

            status._syncTime = {
                timestamp: new Date(),
                position: status.position,
            };
        },

        torrentStatusUpdate: function(torrents) {
            Vue.set(this.torrentModal, 'items', {});

            for (const [url, torrent] of Object.entries(torrents)) {
                Vue.set(this.torrentModal.items, url, torrent);
            }
        },

        onStatusUpdate: function(event) {
            const dev = event.device;
            const status = event.status;
            this.syncPosition(status);

            if (status.state !== 'stop' && this.status[dev.type] && this.status[dev.type][dev.name]) {
                status.title = status.title || this.status[dev.type][dev.name].title;
            }

            if (!this.status[dev.type])
                Vue.set(this.status, dev.type, {});
            Vue.set(this.status[dev.type], dev.name, status);

            if (!this.deviceHandlers[dev.type])
                Vue.set(this.deviceHandlers, dev.type, {});
            Vue.set(this.deviceHandlers[dev.type], dev.name, dev);
        },

        onMediaEvent: async function(event) {
            var type, player;
            const plugin = event.plugin.replace(/^media\./, '');

            if (this.status[event.player] && this.status[event.player][plugin]) {
                type = event.player;
                player = plugin;
            } else if (this.status[plugin] && this.status[plugin][event.player]) {
                type = plugin;
                player = event.player;
            }

            var handler;
            if (this.deviceHandlers[event.player] && this.deviceHandlers[event.player][plugin]) {
                handler = this.deviceHandlers[event.player][plugin];
            } else if (this.deviceHandlers[plugin] && this.deviceHandlers[plugin][event.player]) {
                handler = this.deviceHandlers[plugin][event.player];
            } else {
                // No handlers
                console.warn('No handlers found for device type '.concat(event.plugin, ' and player ', event.player));
                return;
            }

            let status = await handler.status(event.player);
            this.syncPosition(status);

            if (event.resource) {
                event.url = event.resource;
                delete event.resource;
            }

            if (status.state !== 'stop') {
                status.title = status.title || this.status[type][player].title;
            }

            Vue.set(this.status[type], player, status);
        },

        timerFunc: function() {
            for (const [playerType, players] of Object.entries(this.status)) {
                for (const [playerName, status] of Object.entries(players)) {
                    if (status.state === 'play' && !isNaN(status.position) && status._syncTime) {
                        status.position = status._syncTime.position +
                            ((new Date()).getTime()/1000) - (status._syncTime.timestamp.getTime()/1000);
                    }
                }
            }
        },
    },

    created: function() {
        for (const [type, Handler] of Object.entries(MediaHandlers)) {
            MediaHandlers[type] = new Handler();
            MediaHandlers[type].bus = this.bus;
        }

        registerEventHandler(this.onMediaEvent,
            'platypush.message.event.media.NewPlayingMediaEvent',
            'platypush.message.event.media.MediaPlayEvent',
            'platypush.message.event.media.MediaPauseEvent',
            'platypush.message.event.media.MediaStopEvent',
            'platypush.message.event.media.MediaSeekEvent');

        this.bus.$on('play', this.play);
        this.bus.$on('pause', this.pause);
        this.bus.$on('stop', this.stop);
        this.bus.$on('seek', this.seek);
        this.bus.$on('volume', this.setVolume);
        this.bus.$on('info', this.info);
        this.bus.$on('info-loading', this.infoLoading);
        this.bus.$on('selected-device', this.selectDevice);
        this.bus.$on('results-loading', this.onResultsLoading);
        this.bus.$on('results-ready', this.onResultsReady);
        this.bus.$on('status-update', this.onStatusUpdate);
        this.bus.$on('start-streaming', this.startStreaming);
        this.bus.$on('search-subs', this.searchSubs);
        this.bus.$on('torrent-status-update', this.torrentStatusUpdate);

        setInterval(this.timerFunc, 1000);
    },
});


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
            loading: {
                results: false,
                media: false,
            },
        };
    },

    computed: {
        types: function() {
            return MediaHandlers;
        },
    },

    methods: {
        refresh: async function() {
        },

        onResultsLoading: function() {
            this.loading.results = true;
        },

        onResultsReady: function(results) {
            this.loading.results = false;

            for (var i=0; i < results.length; i++) {
                results[i].handler = MediaHandlers[results[i].type];
            }

            this.results = results;
        },

        play: async function(item) {
            if (!this.selectedDevice.accepts[item.type]) {
                item = await this.startStreaming(item.url);
            }

            let status = await this.selectedDevice.play(item.url);

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
            // TODO
            console.log(item);
        },

        startStreaming: async function(item) {
            return await request('media.start_streaming', {
                media: item.url,
            });
        },

        selectDevice: function(device) {
            this.selectedDevice = device;
        },

        syncPosition: function(status) {
            status._syncTime = {
                timestamp: new Date(),
                position: status.position,
            };
        },

        onStatusUpdate: function(event) {
            const dev = event.device;
            const status = event.status;
            this.syncPosition(status);

            if (!this.status[dev.type])
                Vue.set(this.status, dev.type, {});
            Vue.set(this.status[dev.type], dev.name, status);
        },

        onMediaEvent: async function(event) {
            let status = await request(event.plugin + '.status');
            this.syncPosition(status);

            if (event.resource) {
                event.url = event.resource;
                delete event.resource;
            }

            if (event.plugin.startsWith('media.'))
                event.plugin = event.plugin.substr(6);

            if (this.status[event.player] && this.status[event.player][event.plugin])
                Vue.set(this.status[event.player], event.plugin, status);
            else if (this.status[event.plugin] && this.status[event.plugin][event.player])
                Vue.set(this.status[event.plugin], event.player, status);
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
        this.refresh();

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
        this.bus.$on('selected-device', this.selectDevice);
        this.bus.$on('results-loading', this.onResultsLoading);
        this.bus.$on('results-ready', this.onResultsReady);
        this.bus.$on('status-update', this.onStatusUpdate);

        setInterval(this.timerFunc, 1000);
    },
});


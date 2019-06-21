// Will be filled by dynamically loading media type handler scripts
const MediaHandlers = {};

Vue.component('media', {
    template: '#tmpl-media',
    props: ['config','player'],
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

        onStatusUpdate: function(event) {
            const dev = event.device;
            const status = event.status;

            if (!this.status[dev.type])
                Vue.set(this.status, dev.type, {});
            Vue.set(this.status[dev.type], dev.name, status);
        },

        onNewPlayingMedia: function(event) {
            console.log('NEW MEDIA');
            console.log(event);
        },

        onMediaPlay: function(event) {
            console.log('PLAY');
            console.log(event);
        },

        onMediaPause: function(event) {
            console.log('PAUSE');
            console.log(event);
        },

        onMediaStop: function(event) {
            console.log('STOP');
            console.log(event);
        },

        onMediaSeek: function(event) {
            console.log('SEEK');
            console.log(event);
        },
    },

    created: function() {
        this.refresh();

        for (const [type, Handler] of Object.entries(MediaHandlers)) {
            MediaHandlers[type] = new Handler();
            MediaHandlers[type].bus = this.bus;
        }

        registerEventHandler(this.onNewPlayingMedia, 'platypush.message.event.media.NewPlayingMediaEvent');
        registerEventHandler(this.onMediaPlay, 'platypush.message.event.media.MediaPlayEvent');
        registerEventHandler(this.onMediaPause, 'platypush.message.event.media.MediaPauseEvent');
        registerEventHandler(this.onMediaStop, 'platypush.message.event.media.MediaStopEvent');
        registerEventHandler(this.onMediaSeek, 'platypush.message.event.media.MediaSeekEvent');

        this.bus.$on('play', this.play);
        this.bus.$on('info', this.info);
        this.bus.$on('selected-device', this.selectDevice);
        this.bus.$on('results-loading', this.onResultsLoading);
        this.bus.$on('results-ready', this.onResultsReady);
        this.bus.$on('status-update', this.onStatusUpdate);
    },
});


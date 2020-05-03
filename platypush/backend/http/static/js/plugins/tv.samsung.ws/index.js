Vue.component('tv-samsung-ws', {
    template: '#tmpl-tv-samsung-ws',
    data: function() {
        return {};
    },

    methods: {
        up: async function() {
            await request('tv.samsung.ws.up');
        },

        down: async function() {
            await request('tv.samsung.ws.down');
        },

        left: async function() {
            await request('tv.samsung.ws.left');
        },

        right: async function() {
            await request('tv.samsung.ws.right');
        },

        enter: async function() {
            await request('tv.samsung.ws.enter');
        },

        power: async function() {
            await request('tv.samsung.ws.power');
        },

        red: async function() {
            await request('tv.samsung.ws.red');
        },

        yellow: async function() {
            await request('tv.samsung.ws.yellow');
        },

        green: async function() {
            await request('tv.samsung.ws.green');
        },

        blue: async function() {
            await request('tv.samsung.ws.blue');
        },

        volumeUp: async function() {
            await request('tv.samsung.ws.volume_up');
        },

        volumeDown: async function() {
            await request('tv.samsung.ws.volume_down');
        },

        channelUp: async function() {
            await request('tv.samsung.ws.channel_up');
        },

        channelDown: async function() {
            await request('tv.samsung.ws.channel_down');
        },

        mute: async function() {
            await request('tv.samsung.ws.mute');
        },

        home: async function() {
            await request('tv.samsung.ws.home');
        },

        back: async function() {
            await request('tv.samsung.ws.back');
        },

        menu: async function() {
            await request('tv.samsung.ws.menu');
        },

        info: async function() {
            await request('tv.samsung.ws.info');
        },

        source: async function() {
            await request('tv.samsung.ws.source');
        },

        tools: async function() {
            await request('tv.samsung.ws.tools');
        },

        browser: async function() {
            const url = prompt('URL to open').trim();
            if (!url.length) {
                return;
            }

            await request('tv.samsung.ws.open_browser', {'url': url});
        },

        channel: async function() {
            const ch = prompt('Channel number').trim();
            if (!ch.length) {
                return;
            }

            await request('tv.samsung.ws.channel', {channel: parseInt(ch)});
        },

        color: async function(event) {
            await request('tv.samsung.ws.' + event.target.value);
        }
    },
});


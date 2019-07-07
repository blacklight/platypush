Vue.component('music', {
    template: '#tmpl-widget-music',
    props: ['config'],

    data: function() {
        return {
            track: undefined,
            status: undefined,
            timer: undefined,

            syncTime: {
                timestamp: null,
                elapsed: null,
            },
        };
    },

    methods: {
        refresh: async function() {
            let status = await request('music.mpd.status');
            let track = await request('music.mpd.currentsong');

            this._parseStatus(status);
            this._parseTrack(track);

            if (status.state === 'play' && !this.timer)
                this.startTimer();
            else if (status.state !== 'play' && this.timer)
                this.stopTimer();
        },

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

        _parseStatus: async function(status) {
            if (!status || status.length === 0)
                status = await request('music.mpd.status');

            if (!this.status)
                this.status = {};

            for (const [attr, value] of Object.entries(status)) {
                if (['consume','random','repeat','single','bitrate'].indexOf(attr) >= 0) {
                    Vue.set(this.status, attr, !!parseInt(value));
                } else if (['nextsong','nextsongid','playlist','playlistlength',
                            'volume','xfade','song','songid'].indexOf(attr) >= 0) {
                    Vue.set(this.status, attr, parseInt(value));
                } else if (['elapsed'].indexOf(attr) >= 0) {
                    Vue.set(this.status, attr, parseFloat(value));
                } else {
                    Vue.set(this.status, attr, value);
                }
            }
        },

        _parseTrack: async function(track) {
            if (!track || track.length === 0) {
                track = await request('music.mpd.currentsong');
            }

            if (!this.track)
                this.track = {};

            for (const [attr, value] of Object.entries(track)) {
                if (['id','pos','time','track','disc'].indexOf(attr) >= 0) {
                    Vue.set(this.track, attr, parseInt(value));
                } else {
                    Vue.set(this.track, attr, value);
                }
            }
        },

        showNewTrackNotification: function() {
            createNotification({
                html: '<b>' + (this.track.artist || '[No Artist]') + '</b><br>' +
                      (this.track.title || '[No Title]'),
                image: {
                    icon: 'play',
                }
            });
        },

        onNewPlayingTrack: async function(event) {
            let previousTrack = undefined;

            if (this.track) {
                previousTrack = {
                    file: this.track.file,
                    artist: this.track.artist,
                    title: this.track.title,
                };
            }

            this.status.state = 'play';
            Vue.set(this.status, 'elapsed', 0);
            this.track = {};
            this._parseTrack(event.track);

            let status = event.status ? event.status : await request('music.mpd.status');
            this._parseStatus(status);
            this.startTimer();

            if (previousTrack && this.track.file != previousTrack.file
                    || this.track.artist != previousTrack.artist
                    || this.track.title != previousTrack.title) {
                this.showNewTrackNotification();
            }
        },

        onMusicStop: function(event) {
            this.status.state = 'stop';
            Vue.set(this.status, 'elapsed', 0);
            this._parseStatus(event.status);
            this._parseTrack(event.track);
            this.stopTimer();
        },

        onMusicPlay: function(event) {
            this.status.state = 'play';
            this._parseStatus(event.status);
            this._parseTrack(event.track);
            this.startTimer();
        },

        onMusicPause: function(event) {
            this.status.state = 'pause';
            this._parseStatus(event.status);
            this._parseTrack(event.track);

            Vue.set(this.syncTime, 'timestamp', new Date());
            Vue.set(this.syncTime, 'elapsed', this.status.elapsed);
        },

        onSeekChange: function(event) {
            if (event.position != null)
                Vue.set(this.status, 'elapsed', parseFloat(event.position));
            if (event.status)
                this._parseStatus(event.status);
            if (event.track)
                this._parseTrack(event.track);

            Vue.set(this.syncTime, 'timestamp', new Date());
            Vue.set(this.syncTime, 'elapsed', this.status.elapsed);
        },

        onVolumeChange: function(event) {
            if (event.volume != null)
                this.status.volume = parseFloat(event.volume);
            if (event.status)
                this._parseStatus(event.status);
            if (event.track)
                this._parseTrack(event.track);
        },

        onRepeatChange: function(event) {
            this.status.repeat = event.state;
        },

        onRandomChange: function(event) {
            this.status.random = event.state;
        },

        onConsumeChange: function(event) {
            this.status.consume = event.state;
        },

        onSingleChange: function(event) {
            this.status.single = event.state;
        },

        startTimer: function() {
            if (this.timer != null) {
                this.stopTimer();
            }

            Vue.set(this.syncTime, 'timestamp', new Date());
            Vue.set(this.syncTime, 'elapsed', this.status.elapsed);
            this.timer = setInterval(this.timerFunc, 1000);
        },

        stopTimer: function() {
            if (this.timer == null) {
                clearInterval(this.timer);
                this.timer = null;
            }
        },

        timerFunc: function() {
            if (this.status.state !== 'play' || this.status.elapsed == null) {
                return;
            }

            Vue.set(this.status, 'elapsed', this.syncTime.elapsed +
                ((new Date()).getTime()/1000) - (this.syncTime.timestamp.getTime()/1000));
        },
    },

    mounted: function() {
        this.refresh();
        setInterval(this.refresh, 60000);

        registerEventHandler(this.onNewPlayingTrack, 'platypush.message.event.music.NewPlayingTrackEvent');
        registerEventHandler(this.onMusicStop, 'platypush.message.event.music.MusicStopEvent');
        registerEventHandler(this.onMusicPlay, 'platypush.message.event.music.MusicPlayEvent');
        registerEventHandler(this.onMusicPause, 'platypush.message.event.music.MusicPauseEvent');
        registerEventHandler(this.onSeekChange, 'platypush.message.event.music.SeekChangeEvent');
        registerEventHandler(this.onVolumeChange, 'platypush.message.event.music.VolumeChangeEvent');
        registerEventHandler(this.onRepeatChange, 'platypush.message.event.music.PlaybackRepeatModeChangeEvent');
        registerEventHandler(this.onRandomChange, 'platypush.message.event.music.PlaybackRandomModeChangeEvent');
        registerEventHandler(this.onConsumeChange, 'platypush.message.event.music.PlaybackConsumeModeChangeEvent');
        registerEventHandler(this.onSingleChange, 'platypush.message.event.music.PlaybackSingleModeChangeEvent');
    },
});


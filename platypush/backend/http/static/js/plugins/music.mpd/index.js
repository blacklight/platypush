Vue.component('music-mpd', {
    template: '#tmpl-music-mpd',
    props: ['config'],
    data: function() {
        return {
            track: {},
            status: {},
            playlist: [],
            timer: null,
            browserPath: [],
            browserItems: [],
            syncTime: {
                timestamp: null,
                elapsed: null,
            },
        };
    },

    methods: {
        refresh: async function() {
            const getStatus = request('music.mpd.status');
            const getTrack = request('music.mpd.currentsong');
            const getPlaylist = request('music.mpd.playlistinfo');
            const getBrowserItems = request('music.mpd.lsinfo');

            let [status, track, playlist, browserItems] = await Promise.all([getStatus, getTrack, getPlaylist, getBrowserItems]);

            this._parseStatus(status);
            this._parseTrack(track);
            this._parsePlaylist(playlist);
            this._parseBrowserItems(browserItems);

            if (this.status.state === 'play') {
                this.startTimer();
            }
        },

        _parseStatus: async function(status) {
            if (!status || status.length === 0) {
                status = await request('music.mpd.status');
            }

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

            for (const [attr, value] of Object.entries(track)) {
                if (['id','pos','time'].indexOf(attr) >= 0) {
                    Vue.set(this.track, attr, parseInt(value));
                } else {
                    Vue.set(this.track, attr, value);
                }
            }
        },

        _parsePlaylist: function(playlist) {
            if (!playlist || playlist.length === 0) {
                return;
            }

            this.playlist = [];

            for (var track of playlist) {
                for (const [attr, value] of Object.entries(track)) {
                    if (['time','pos','id'].indexOf(attr) >= 0) {
                        track[attr] = parseInt(value);
                    } else {
                        track[attr] = value;
                    }
                }

                this.playlist.push(track);
            }
        },

        _parseBrowserItems: function(browserItems) {
            if (!browserItems || browserItems.length === 0) {
                return;
            }

            this.browserItems = [];

            for (var item of browserItems) {
                if (item.directory) {
                    this.browserItems.push({
                        type: 'directory',
                        name: item.directory,
                    });
                } else if (item.playlist) {
                    this.browserItems.push({
                        type: 'playlist',
                        name: item.playlist,
                        'last-modified': item['last-modified'],
                    });
                }
            }
        },

        convertTime: function(time) {
            time = parseFloat(time);   // Normalize strings
            var t = {};
            t.h = '' + parseInt(time/3600);
            t.m = '' + parseInt(time/60 - t.h*60);
            t.s = '' + parseInt(time - t.m*60);

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

        previous: async function() {
            await request('music.mpd.previous');
            let track = await request('music.mpd.currentsong');
            this.onNewPlayingTrack({track: track});
        },

        repeat: async function() {
            await request('music.mpd.repeat');
            let status = await request('music.mpd.status');
            this._parseStatus(status);
        },

        playPause: async function() {
            await request('music.mpd.pause');
            let status = await request('music.mpd.status');
            const method = status.state === 'play' ? this.onMusicPlay : this.onMusicPause;
            method({ status: status });
        },

        stop: async function() {
            await request('music.mpd.stop');
            this.onMusicStop({});
        },

        random: async function() {
            await request('music.mpd.random');
            let status = await request('music.mpd.status');
            this._parseStatus(status);
        },

        next: async function() {
            await request('music.mpd.next');
            let track = await request('music.mpd.currentsong');
            this.onNewPlayingTrack({track: track});
        },

        seek: async function(event) {
            var value;

            if (event.target) {
                value = parseFloat(event.target.value);
            } else if (event.value) {
                value = parseFloat(event.value);
            } else {
                value = parseFloat(event);
            }

            const status = await request('music.mpd.seekcur', {value: value});
            this.onSeekChange({status: status});
        },

        volume: async function(event) {
            var value;

            if (event.target) {
                value = parseFloat(event.target.value);
            } else if (event.value) {
                value = parseFloat(event.value);
            } else {
                value = parseFloat(event);
            }

            const status = await request('music.mpd.setvol', {vol: value});
            this.onVolumeChange({status: status});
        },

        onNewPlayingTrack: async function(event) {
            var previousTrack = {
                file: this.track.file,
                artist: this.track.artist,
                title: this.track.title,
            };

            this.status.state = 'play';
            this.status.elapsed = 0;
            this.track = {};

            let status = await request('music.mpd.status');
            this._parseStatus(status);
            this._parseTrack(event.track);
            this.startTimer();

            if (this.track.file != previousTrack.file
                    || this.track.artist != previousTrack.artist
                    || this.track.title != previousTrack.title) {
                this.showNewTrackNotification();
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

        onMusicStop: function(event) {
            this.status.state = 'stop';
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

            this.syncTime.timestamp = new Date();
            this.syncTime.elapsed = this.status.elapsed;
        },

        onSeekChange: function(event) {
            if (event.position != null)
                this.status.elapsed = parseFloat(event.position);
            if (event.status)
                this._parseStatus(event.status);
            if (event.track)
                this._parseTrack(event.track);

            this.syncTime.timestamp = new Date();
            this.syncTime.elapsed = this.status.elapsed;
        },

        onPlaylistChange: function(event) {
            console.log(event);
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

        startTimer: function() {
            if (this.timer != null) {
                this.stopTimer();
            }

            this.syncTime.timestamp = new Date();
            this.syncTime.elapsed = this.status.elapsed;
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

            this.status.elapsed = this.syncTime.elapsed +
                ((new Date()).getTime()/1000) - (this.syncTime.timestamp.getTime()/1000);
        },
    },

    created: function() {
        this.refresh();
        registerEventHandler(this.onNewPlayingTrack, 'platypush.message.event.music.NewPlayingTrackEvent');
        registerEventHandler(this.onMusicStop, 'platypush.message.event.music.MusicStopEvent');
        registerEventHandler(this.onMusicPlay, 'platypush.message.event.music.MusicPlayEvent');
        registerEventHandler(this.onMusicPause, 'platypush.message.event.music.MusicPauseEvent');
        registerEventHandler(this.onSeekChange, 'platypush.message.event.music.SeekChangeEvent');
        registerEventHandler(this.onPlaylistChange, 'platypush.message.event.music.PlaylistChangeEvent');
        registerEventHandler(this.onVolumeChange, 'platypush.message.event.music.VolumeChangeEvent');
        registerEventHandler(this.onRepeatChange, 'platypush.message.event.music.PlaybackRepeatModeChangeEvent');
        registerEventHandler(this.onRandomChange, 'platypush.message.event.music.PlaybackRandomModeChangeEvent');
    },
});


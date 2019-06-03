Vue.component('music-mpd', {
    template: '#tmpl-music-mpd',
    props: ['config'],
    data: function() {
        return {
            track: {},
            status: {},
            timer: null,
            playlist: [],
            playlistFilter: '',
            browserFilter: '',
            browserPath: [],
            browserItems: [],

            selectionMode: {
                playlist: false,
                browser: false,
            },

            selectedPlaylistItems: {},
            selectedBrowserItems: {},

            syncTime: {
                timestamp: null,
                elapsed: null,
            },

            newTrackLock: false,
        };
    },

    computed: {
        playlistDropdownItems: function() {
            var self = this;
            var items = [];

            if (Object.keys(this.selectedPlaylistItems).length === 1) {
                items.push({
                    text: 'Play',
                    icon: 'play',
                    click: async function() {
                        await self.playpos();
                        self.selectedPlaylistItems = {};
                    },
                });
            }

            items.push(
                {
                    text: 'Add to playlist',
                    icon: 'list',
                },
                {
                    text: 'Move',
                    icon: 'retweet',
                },
                {
                    text: 'Remove from queue',
                    icon: 'trash',
                    click: async function() {
                        await self.del();
                        self.selectedPlaylistItems = {};
                    },
                },
            );

            if (Object.keys(this.selectedPlaylistItems).length === 1) {
                items.push({
                    text: 'View track info',
                    icon: 'info',
                });
            }

            return items;
        },

        browserDropdownItems: function() {
            var self = this;
            var items = [];

            if (Object.keys(this.selectedBrowserItems).length === 1 &&
                    Object.values(this.selectedBrowserItems)[0].type === 'directory') {
                items.push({
                    text: 'Open',
                    icon: 'folder',
                    click: async function() {
                        await self.cd();
                        self.selectedBrowserItems = {};
                    },
                });
            }

            if (Object.keys(this.selectedBrowserItems).length === 1) {
                items.push(
                    {
                        text: 'Add and play',
                        icon: 'play',
                        click: async function() {
                            const item = Object.values(self.selectedBrowserItems)[0];
                            var promise;

                            switch (item.type) {
                                case 'playlist':
                                    promise = self.load(item.name);
                                    break;
                                case 'file':
                                    promise = self.add(item.name, position=0);
                                    break;
                                case 'directory':
                                    promise = self.add(item.name);
                                    break;
                                default:
                                    console.warning('Unable to handle type: ' + item.type);
                                    break;
                            }

                            await promise;
                            await self.playpos(0);
                            self.selectedBrowserItems = {};
                        },
                    },
                    {
                        text: 'Replace and play',
                        icon: 'play',
                        click: async function() {
                            await self.clear();

                            const item = Object.values(self.selectedBrowserItems)[0];
                            var promise;

                            switch (item.type) {
                                case 'playlist':
                                    promise = self.load(item.name);
                                    break;
                                case 'file':
                                    promise = self.add(item.name, position=0);
                                    break;
                                case 'directory':
                                    promise = self.add(item.name);
                                    break;
                                default:
                                    console.warning('Unable to handle type: ' + item.type);
                                    break;
                            }

                            await promise;
                            await self.playpos(0);
                            self.selectedBrowserItems = {};
                        },
                    }
                );
            }

            items.push(
                {
                    text: 'Add to queue',
                    icon: 'plus',
                    click: async function() {
                        const items = Object.values(self.selectedBrowserItems);
                        const promises = items.map(item => item.type === 'playlist' ? self.load(item.name) : self.add(item.name));

                        await Promise.all(promises);
                        self.selectedBrowserItems = {};
                    },
                },
            );

            if (Object.keys(this.selectedBrowserItems).length === 1
                    && Object.values(this.selectedBrowserItems)[0].type === 'playlist') {
                items.push({
                    text: 'Edit',
                    icon: 'pen',
                });
            }

            if (Object.values(this.selectedBrowserItems).filter(item => item.type === 'playlist').length === Object.values(this.selectedBrowserItems).length) {
                items.push({
                    text: 'Remove',
                    icon: 'trash',
                    click: async function() {
                        if (!confirm('Are you sure you want to remove the selected playlist' +
                                (Object.values(self.selectedBrowserItems).length > 1 ? 's' : '') + '?')) {
                            return;
                        }

                        const items = Object.values(self.selectedBrowserItems);
                        await self.rm(items);
                        self.selectedBrowserItems = {};
                    },
                });
            }

            if (Object.keys(this.selectedBrowserItems).length === 1
                    && Object.values(this.selectedBrowserItems)[0].type === 'file') {
                items.push({
                    text: 'View info',
                    icon: 'info',
                });
            }

            return items;
        },
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

        // Hack-ish workaround to get the browser and playlist panels to keep their height
        // in sync with the nav and control bars, as both those elements are fixed.
        adjustLayout: function() {
            const adjust = (self) => {
                const nav = document.querySelector('nav');
                const panels = document.querySelectorAll('.music-mpd-container .panels .panel');
                const controls = document.querySelector('.music-mpd-container .controls');

                return () => {
                    const panelHeight = window.innerHeight - nav.clientHeight - controls.clientHeight - 5;
                    if (panelHeight >= 0) {
                        for (const panel of panels) {
                            if (panelHeight != parseFloat(panel.style.height)) {
                                panel.style.height = panelHeight + 'px';
                            }
                        }
                    }
                }
            };

            adjust(this)();
            setInterval(adjust(this), 2000);
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
                        id: 'directory:' + item.directory,
                        type: 'directory',
                        name: item.directory,
                    });
                } else if (item.playlist) {
                    this.browserItems.push({
                        id: 'playlist:' + item.playlist,
                        type: 'playlist',
                        name: item.playlist,
                        'last-modified': item['last-modified'],
                    });
                } else if (item.file) {
                    this.browserItems.push({
                        id: item.file,
                        type: 'file',
                        name: item.file,
                        ...item,
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

        consume: async function() {
            await request('music.mpd.consume');
            let status = await request('music.mpd.status');
            this._parseStatus(status);
        },

        single: async function() {
            await request('music.mpd.single');
            let status = await request('music.mpd.status');
            this._parseStatus(status);
        },

        playPause: async function() {
            await request('music.mpd.pause');
            let status = await request('music.mpd.status');
            const method = status.state === 'play' ? this.onMusicPlay : this.onMusicPause;
            method({ status: status });
        },

        playpos: async function(pos) {
            if (pos == null) {
                if (!Object.keys(this.selectedPlaylistItems).length) {
                    return;
                }

                pos = Object.keys(this.selectedPlaylistItems)[0];
            }

            let status = await request('music.mpd.play_pos', {pos: pos});
            this._parseStatus(status);

            let track = await request('music.mpd.currentsong');
            this._parseTrack(track);
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

        clear: async function() {
            if (!confirm('Are you sure that you want to clear the playlist?')) {
                return;
            }

            await request('music.mpd.clear');
            this.stopTimer();
            this.track = {};
            this.playlist = [];

            let status = await request('music.mpd.status');
            this._parseStatus(status);
        },

        add: async function(resource, position=null) {
            var args = {resource: resource};
            if (position != null) {
                args.position = position;
            }

            let status = await request('music.mpd.add', args);
            this._parseStatus(status);

            let playlist = await request('music.mpd.playlistinfo');
            this._parsePlaylist(playlist);
        },

        load: async function(item) {
            let status = await request('music.mpd.load', {playlist:item});
            this._parseStatus(status);

            let playlist = await request('music.mpd.playlistinfo');
            this._parsePlaylist(playlist);
        },

        del: async function() {
            const positions = Object.keys(this.selectedPlaylistItems);
            if (!positions.length) {
                return;
            }

            let status = await request('music.mpd.delete', {'positions': positions});
            this._parseStatus(status);

            for (const pos in positions) {
                Vue.delete(this.selectedPlaylistItems, pos);
            }
        },

        rm: async function(items) {
            if (!items) {
                items = Object.values(this.selectedBrowserItems);
            }

            if (!items.length) {
                return;
            }

            let status = await request('music.mpd.rm', {playlist: items.map(_ => _.name)});
            this._parseStatus(status);

            items = await request('music.mpd.lsinfo', {uri: this.browserPath.join('/')});
            this._parseBrowserItems(items);
        },

        swap: async function() {
            if (Object.keys(this.selectedPlaylistItems).length !== 2) {
                return;
            }

            const positions = Object.keys(this.selectedPlaylistItems).sort();
            await request('music.mpd.move', {from_pos: positions[1], to_pos: positions[0]});

            let status = await request('music.mpd.move', {from_pos: positions[0]+1, to_pos: positions[1]});
            this._parseStatus(status);

            const playlist = await request('music.mpd.playlistinfo');
            this._parsePlaylist(playlist);
        },

        cd: async function() {
            const item = Object.values(this.selectedBrowserItems)[0];

            if (item.name === '..') {
                if (this.browserPath.length) {
                    this.browserPath.pop();
                }
            } else {
                this.browserPath = item.name.split('/');
            }

            const items = await request('music.mpd.lsinfo', {uri: this.browserPath.join('/')});
            this._parseBrowserItems(items);
        },

        onNewPlayingTrack: async function(event) {
            var previousTrack = {
                file: this.track.file,
                artist: this.track.artist,
                title: this.track.title,
            };

            this.status.state = 'play';
            Vue.set(this.status, 'elapsed', 0);
            this.track = {};
            this._parseTrack(event.track);

            let status = event.status ? event.status : await request('music.mpd.status');
            this._parseStatus(status);
            this.startTimer();

            if (this.track.file != previousTrack.file
                    || this.track.artist != previousTrack.artist
                    || this.track.title != previousTrack.title) {
                this.showNewTrackNotification();

                const self = this;
                setTimeout(function() {
                    self.scrollToActiveTrack();
                }, 100);
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

        onPlaylistChange: async function(event) {
            if (event.changes) {
                this.playlist = event.changes;
            } else {
                const playlist = await request('music.mpd.playlistinfo');
                this._parsePlaylist(playlist);
            }
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

        matchesPlaylistFilter: function(track) {
            if (this.playlistFilter.length === 0)
                return true;

            return [track.artist || '', track.title || '', track.album || '']
                .join(' ').toLocaleLowerCase().indexOf(
                    this.playlistFilter.split(' ').filter(_ => _.length > 0).map(_ => _.toLocaleLowerCase()).join(' ')
                ) >= 0;
        },

        matchesBrowserFilter: function(item) {
            if (this.browserFilter.length === 0)
                return true;

            return item.name.toLocaleLowerCase().indexOf(
                this.browserFilter.toLocaleLowerCase().split(' ').filter(_ => _.length > 0).join(' ')) >= 0;
        },

        onPlaylistItemClick: function(track) {
            if (this.selectionMode.playlist) {
                if (track.pos in this.selectedPlaylistItems) {
                    Vue.delete(this.selectedPlaylistItems, track.pos);
                } else {
                    Vue.set(this.selectedPlaylistItems, track.pos, track);
                }
            } else if (track.pos in this.selectedPlaylistItems) {
                Vue.delete(this.selectedPlaylistItems, track.pos);
            } else {
                this.selectedPlaylistItems = {};
                Vue.set(this.selectedPlaylistItems, track.pos, track);
                openDropdown(this.$refs.playlistDropdown.$el);
            }
        },

        onBrowserItemClick: function(item) {
            if (item.type === 'directory' && item.name === '..') {
                this.selectedBrowserItems = {};
                this.selectedBrowserItems[item.id] = item;
                this.cd();
                this.selectedBrowserItems = {};
                return;
            }

            if (this.selectionMode.browser) {
                if (item.id in this.selectedBrowserItems) {
                    Vue.delete(this.selectedBrowserItems, item.id);
                } else {
                    Vue.set(this.selectedBrowserItems, item.id, item);
                }
            } else if (item.id in this.selectedBrowserItems) {
                Vue.delete(this.selectedBrowserItems, item.id);
            } else {
                this.selectedBrowserItems = {};
                Vue.set(this.selectedBrowserItems, item.id, item);
                openDropdown(this.$refs.browserDropdown.$el);
            }
        },

        togglePlaylistSelectionMode: function() {
            if (this.selectionMode.playlist && Object.keys(this.selectedPlaylistItems).length) {
                openDropdown(this.$refs.playlistDropdown.$el);
            }

            this.selectionMode.playlist = !this.selectionMode.playlist;
        },

        playlistSelectAll: function() {
            this.selectedPlaylistItems = {};
            this.selectionMode.playlist = true;

            for (var track of this.playlist) {
                this.selectedPlaylistItems[track.pos] = track;
            }

            openDropdown(this.$refs.playlistDropdown.$el);
        },

        toggleBrowserSelectionMode: function() {
            if (this.selectionMode.browser && Object.keys(this.selectedBrowserItems).length) {
                openDropdown(this.$refs.browserDropdown.$el);
            }

            this.selectionMode.browser = !this.selectionMode.browser;
        },

        browserSelectAll: function() {
            this.selectedBrowserItems = {};
            this.selectionMode.browser = true;

            for (var item of this.browserItems) {
                if (item.type !== 'directory' && item.name !== '..') {
                    this.selectedBrowserItems[item.id] = item;
                }
            }

            openDropdown(this.$refs.browserDropdown.$el);
        },

        scrollToActiveTrack: function() {
            if (this.$refs.activePlaylistTrack && this.$refs.activePlaylistTrack.length) {
                this.$refs.activePlaylistTrack[0].$el.scrollIntoView({behavior: 'smooth'});
            }
        },

        addToPlaylistPrompt: async function() {
            var resource = prompt('Path or URI of the resource to add');
            if (!resource.length) {
                return;
            }

            this.add(resource);
        },

        savePlaylistPrompt: async function() {
            var name = prompt('Playlist name');
            if (!name.length) {
                return;
            }

            let status = await request('music.mpd.save', {name: name});
            this._parseStatus(status);

            let items = await request('music.mpd.lsinfo', {uri: this.browserPath.join('/')});
            this._parseBrowserItems(items);
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
        registerEventHandler(this.onConsumeChange, 'platypush.message.event.music.PlaybackConsumeModeChangeEvent');
        registerEventHandler(this.onSingleChange, 'platypush.message.event.music.PlaybackSingleModeChangeEvent');
    },

    mounted: function() {
        this.adjustLayout();
        this.scrollToActiveTrack();
    },
});


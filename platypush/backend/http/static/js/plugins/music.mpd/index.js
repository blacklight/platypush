Vue.component('music-mpd', {
    template: '#tmpl-music-mpd',
    props: ['config'],
    mixins: [utils],
    data: function() {
        return {
            track: {},
            status: {},
            timer: null,
            playlist: [],
            playlists: [],
            playlistFilter: '',
            browserFilter: '',
            playlistAddFilter: '',
            editorFilter: '',
            browserPath: [],
            browserItems: [],

            selectionMode: {
                playlist: false,
                browser: false,
                editor: false,
            },

            moveMode: {
                playlist: false,
                editor: false,
            },

            infoItem: {},
            modalVisible: {
                info: false,
                editor: false,
                playlistAdd: false,
            },

            addToPlaylistItems: [],
            selectedPlaylist: {},
            selectedPlaylistItems: {},
            selectedPlaylistAddItems: {},
            selectedEditorItems: {},
            selectedBrowserItems: {},

            syncTime: {
                timestamp: null,
                elapsed: null,
            },
        };
    },

    computed: {
        playlistDropdownItems: function() {
            var self = this;
            var items = [];

            if (Object.keys(this.selectedPlaylistItems).length === 1) {
                const track = Object.values(this.selectedPlaylistItems)[0];

                items.push({
                        text: 'Play',
                        icon: 'play',
                        click: async function() {
                            await self.playpos();
                            self.selectedPlaylistItems = {};
                        },
                    }
                );

                if (track.artist && track.artist.length) {
                    items.push({
                        text: 'View artist',
                        icon: 'user',
                        click: async function() {
                            await self.searchArtist(track);
                            self.selectedPlaylistItems = {};
                        }
                    });
                }

                if (track.album && track.album.length) {
                    items.push({
                        text: 'View album',
                        icon: 'compact-disc',
                        click: async function() {
                            await self.searchAlbum(track);
                            self.selectedPlaylistItems = {};
                        },
                    });
                }
            }

            items.push({
                text: 'Add to playlist',
                icon: 'list',
                click: async function() {
                    self.addToPlaylistItems = Object.values(self.selectedPlaylistItems).map(_ => _.file);
                    self.selectedPlaylistItems = {};
                    self.modalVisible.playlistAdd = true;
                    await self.listplaylists();
                },
            });

            if (Object.keys(this.selectedPlaylistItems).length < this.playlist.length) {
                items.push({
                    text: 'Move',
                    icon: 'retweet',
                    click: function() {
                        self.moveMode.playlist = true;
                    },
                });
            }

            items.push({
                text: 'Remove from queue',
                icon: 'trash',
                click: async function() {
                    await self.del();
                    self.selectedPlaylistItems = {};
                },
            });

            if (Object.keys(this.selectedPlaylistItems).length === 1) {
                items.push({
                    text: 'View track info',
                    icon: 'info',
                    click: async function() {
                        await self.info(Object.values(self.selectedPlaylistItems)[0]);
                    },
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
                const item = Object.values(this.selectedBrowserItems)[0];

                items.push(
                    {
                        text: 'Play',
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

                if (item.artist && item.artist.length) {
                    items.push({
                        text: 'View artist',
                        icon: 'user',
                        click: async function() {
                            await self.searchArtist(item);
                            self.selectedBrowserItems = {};
                        }
                    });
                }

                if (item.album && item.album.length) {
                    items.push({
                        text: 'View album',
                        icon: 'compact-disc',
                        click: async function() {
                            await self.searchAlbum(item);
                            self.selectedBrowserItems = {};
                        },
                    });
                }
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

            if (Object.values(this.selectedBrowserItems).filter(_ => _.type === 'file').length === Object.values(this.selectedBrowserItems).length) {
                items.push(
                    {
                        text: 'Add to playlist',
                        icon: 'list',
                        click: async function() {
                            self.addToPlaylistItems = Object.keys(self.selectedBrowserItems);
                            self.modalVisible.playlistAdd = true;
                            await self.listplaylists();
                            self.selectedBrowserItems = {};
                        },
                    },
                );
            }

            if (Object.keys(this.selectedBrowserItems).length === 1
                    && Object.values(this.selectedBrowserItems)[0].type === 'playlist') {
                items.push({
                    text: 'Edit',
                    icon: 'pen',
                    click: async function() {
                        const item = Object.values(self.selectedBrowserItems)[0];
                        self.selectedPlaylist.name = item.name;
                        await self.refreshSelectedPlaylist();
                        self.modalVisible.editor = true;
                        self.selectedBrowserItems = {};
                    },
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
                    click: async function() {
                        await self.info(Object.values(self.selectedBrowserItems)[0].name);
                    },
                });
            }

            return items;
        },

        editorDropdownItems: function() {
            var self = this;
            var items = [];

            if (Object.keys(this.selectedEditorItems).length === 1) {
                const item = Object.values(this.selectedEditorItems)[0];

                items.push(
                    {
                        text: 'Play',
                        icon: 'play',
                        click: async function() {
                            await self.add(item.file, position=0);
                            await self.playpos(0);
                            self.selectedEditorItems = {};
                        },
                    },
                    {
                        text: 'Replace and play',
                        icon: 'play',
                        click: async function() {
                            await self.clear();
                            await self.add(item.file, position=0);
                            await self.playpos(0);
                            self.selectedEditorItems = {};
                        },
                    }
                );

                if (item.artist && item.artist.length) {
                    items.push({
                        text: 'View artist',
                        icon: 'user',
                        click: async function() {
                            await self.searchArtist(item);
                            self.selectedEditorItems = {};
                        }
                    });
                }

                if (item.album && item.album.length) {
                    items.push({
                        text: 'View album',
                        icon: 'compact-disc',
                        click: async function() {
                            await self.searchAlbum(item);
                            self.selectedEditorItems = {};
                        },
                    });
                }
            }

            items.push(
                {
                    text: 'Add to queue',
                    icon: 'plus',
                    click: async function() {
                        const items = Object.values(self.selectedEditorItems);
                        const promises = items.map(item => self.add(item.file));

                        await Promise.all(promises);
                        self.selectedEditorItems = {};
                    },
                },
                {
                    text: 'Add to playlist',
                    icon: 'list',
                    click: async function() {
                        self.addToPlaylistItems = Object.keys(self.selectedEditorItems);
                        self.modalVisible.playlistAdd = true;
                        await self.listplaylists();
                        self.selectedEditorItems = {};
                    },
                }
            );

            if (Object.keys(this.selectedEditorItems).length < this.selectedPlaylist.items.length) {
                items.push({
                    text: 'Move',
                    icon: 'retweet',
                    click: function() {
                        self.moveMode.editor = true;
                    },
                });
            }

            items.push(
                {
                    text: 'Remove',
                    icon: 'trash',
                    click: async function() {
                        if (!confirm('Are you sure you want to remove the selected track' +
                                (Object.values(self.selectedEditorItems).length > 1 ? 's' : '') + ' from the playlist?')) {
                            return;
                        }

                        const items = Object.values(self.selectedEditorItems);
                        await self.playlistdelete(items.map(_ => _.pos));
                        self.selectedEditorItems = {};
                    },
                }
            );

            if (Object.keys(this.selectedEditorItems).length === 1) {
                const item = Object.values(self.selectedEditorItems)[0];

                items.push({
                    text: 'View info',
                    icon: 'info',
                    click: async function() {
                        await self.info(item.file);
                    },
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
                if (['id','pos','time','track','disc'].indexOf(attr) >= 0) {
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
                    if (['time','pos','id','track','disc'].indexOf(attr) >= 0) {
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

        load: async function(item, play=false) {
            await request('music.mpd.load', {playlist:item, play:play});
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

        move: async function(fromPos, toPos, updateChanges=true) {
            let status = await request('music.mpd.move', {from_pos: fromPos, to_pos: toPos});

            if (updateChanges) {
                this._parseStatus(status);
                const playlist = await request('music.mpd.playlistinfo');
                this._parsePlaylist(playlist);
            }
        },

        playlistmove: async function(fromPos, toPos) {
            if (!this.selectedPlaylist.name) {
                return;
            }

            await request('music.mpd.playlistmove', {name: this.selectedPlaylist.name, from_pos: fromPos, to_pos: toPos});
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

        info: async function(item) {
            var info = item;

            if (typeof(item) === 'string') {
                var items = await request('music.mpd.search', {filter: {file: info}});
                item = items.length ? items[0] : {file: info};
            }

            this.infoItem = item;
            this.modalVisible.info = true;
        },

        searchArtist: async function(item) {
            await this.search({artist: item.artist});
        },

        searchAlbum: async function(item) {
            var query = {};

            if (item['x-albumuri']) {
                query.file = item['x-albumuri'];
            } else {
                query.artist = item.albumartist || item.artist;
                query.album = item.album;
            }

            await this.search(query);
        },

        search: async function(query) {
            this.$refs.search.resetQuery();
            this.$refs.search.query = query;
            this.$refs.search.visible = true;
            await this.$refs.search.search();
        },

        listplaylists: async function() {
            this.playlists = [];
            let playlists = await request('music.mpd.listplaylists');

            for (const p of playlists) {
                this.playlists.push(p);
            }
        },

        listplaylist: async function(name) {
            return await request('music.mpd.listplaylist', {name: name});
        },

        listplaylistinfo: async function(name) {
            return await request('music.mpd.listplaylistinfo', {name: name});
        },

        playlistadd: async function(items=[], playlists=[]) {
            if (!playlists.length) {
                if (this.modalVisible.playlistAdd) {
                    playlists = Object.keys(this.selectedPlaylistAddItems);
                }
            }

            if (!items.length) {
                items = this.addToPlaylistItems;
            }

            if (!items.length || !playlists.length) {
                return;
            }

            var promises = [];
            for (const playlist of playlists) {
                promises.push(request('music.mpd.playlistadd', {
                    name: playlist, uri: items.map(_ => typeof(_) === 'object' ? _.file : _)
                }));
            }

            await Promise.all(promises);
            this.modalVisible.playlistAdd = false;
            this.addToPlaylistItems = [];
        },

        playlistdelete: async function(items=[]) {
            if (!items.length) {
                items = Object.keys(this.selectedEditorItems);
            }

            if (!items.length || !this.selectedPlaylist.name) {
                return;
            }

            await request('music.mpd.playlistdelete', {name: this.selectedPlaylist.name, pos: items});
            await this.refreshSelectedPlaylist();
        },

        playlistclear: async function() {
            if (!confirm('Are you sure that you want to clear this playlist? This operation is NOT REVERSIBLE')) {
                return;
            }

            await request('music.mpd.playlistclear', {name: this.selectedPlaylist.name});
            await this.refreshSelectedPlaylist();
        },

        rename: async function() {
            if (!this.selectedPlaylist.name) {
                return;
            }

            var newName = prompt('New name for the playlist', this.selectedPlaylist.name);
            if (!newName.length) {
                return;
            }

            await request('music.mpd.rename', {name: this.selectedPlaylist.name, new_name: newName});
            await this.listplaylists();

            for (var item of this.browserItems) {
                if (item.type === 'playlist' && item.name === this.selectedPlaylist.name) {
                    item.name = newName;
                }
            }

            this.selectedPlaylist.name = newName;
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

            const filter = this.playlistFilter.split(' ').filter(_ => _.length > 0).map(_ => _.toLocaleLowerCase()).join(' ');
            return [track.artist || '', track.title || '', track.album || ''].join(' ').toLocaleLowerCase().indexOf(filter) >= 0;
        },

        matchesEditorFilter: function(track) {
            if (this.editorFilter.length === 0)
                return true;

            const filter = this.editorFilter.split(' ').filter(_ => _.length > 0).map(_ => _.toLocaleLowerCase()).join(' ');
            return [track.artist || '', track.title || '', track.album || ''].join(' ').toLocaleLowerCase().indexOf(filter) >= 0;
        },

        matchesBrowserFilter: function(item) {
            if (this.browserFilter.length === 0)
                return true;

            const filter = this.browserFilter.toLocaleLowerCase().split(' ').filter(_ => _.length > 0).join(' ');
            return (item.artist || '').concat(item.name).toLocaleLowerCase().indexOf(filter) >= 0;
        },

        matchesPlaylistAddFilter: function(item) {
            if (this.playlistAddFilter.length === 0)
                return true;

            const filter = this.playlistAddFilter.toLocaleLowerCase().split(' ').filter(_ => _.length > 0).join(' ');
            return (item.playlist || '').toLocaleLowerCase().indexOf(filter) >= 0;
        },

        onPlaylistItemClick: async function(track) {
            if (this.selectionMode.playlist) {
                if (track.pos in this.selectedPlaylistItems) {
                    Vue.delete(this.selectedPlaylistItems, track.pos);
                } else {
                    Vue.set(this.selectedPlaylistItems, track.pos, track);
                }
            } else if (this.moveMode.playlist) {
                var fromPos = Object.values(this.selectedPlaylistItems).map(_ => _.pos);
                var toPos = track.pos;
                this.moveMode.playlist = false;

                const promises = fromPos.map((pos,i) => this.move(pos, toPos+i, false));
                await Promise.all(promises);
                this.selectedPlaylistItems = {};

                const playlist = await request('music.mpd.playlistinfo');
                this._parsePlaylist(playlist);
            } else if (track.pos in this.selectedPlaylistItems) {
                Vue.delete(this.selectedPlaylistItems, track.pos);
            } else {
                this.selectedPlaylistItems = {};
                Vue.set(this.selectedPlaylistItems, track.pos, track);
                openDropdown(this.$refs.playlistDropdown.$el);
            }
        },

        onEditorItemClick: async function(track) {
            if (this.selectionMode.editor) {
                if (track.pos in this.selectedEditorItems) {
                    Vue.delete(this.selectedEditorItems, track.pos);
                } else {
                    Vue.set(this.selectedEditorItems, track.pos, track);
                }
            } else if (this.moveMode.editor) {
                var fromPos = Object.values(this.selectedEditorItems).map(_ => _.pos);
                var toPos = track.pos;
                this.moveMode.editor = false;

                const promises = fromPos.map((pos,i) => this.playlistmove(pos, toPos+i));
                await Promise.all(promises);
                await this.refreshSelectedPlaylist();
            } else if (track.pos in this.selectedEditorItems) {
                Vue.delete(this.selectedEditorItems, track.pos);
            } else {
                this.selectedEditorItems = {};
                Vue.set(this.selectedEditorItems, track.pos, track);
                openDropdown(this.$refs.editorDropdown.$el);
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

        onPlaylistAddItemClick: function(playlist) {
            if (playlist.playlist in this.selectedPlaylistAddItems) {
                Vue.delete(this.selectedPlaylistAddItems, playlist.playlist);
            } else {
                Vue.set(this.selectedPlaylistAddItems, playlist.playlist, playlist);
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

        toggleEditorSelectionMode: function() {
            if (this.selectionMode.editor && Object.keys(this.selectedEditorItems).length) {
                openDropdown(this.$refs.editorDropdown.$el);
            }

            this.selectionMode.editor = !this.selectionMode.editor;
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

        editorSelectAll: function() {
            this.selectedEditorItems = {};
            this.selectionMode.editor = true;

            for (var item of this.selectedPlaylist.items) {
                Vue.set(this.selectedEditorItems, item.pos, item);
            }

            openDropdown(this.$refs.editorDropdown.$el);
        },

        scrollToActiveTrack: function() {
            if (this.$refs.activePlaylistTrack && this.$refs.activePlaylistTrack.length) {
                this.$refs.activePlaylistTrack[0].$el.scrollIntoView({behavior: 'smooth'});
            } else {
                return;
            }
        },

        addToPlaylistPrompt: async function() {
            var resource = prompt('Path or URI of the resource to add');
            if (!resource.length) {
                return;
            }

            await this.add(resource);
        },

        addToPlaylistEditorPrompt: async function() {
            var resource = prompt('Path or URI of the resource to add');
            if (!resource.length) {
                return;
            }

            await request('music.mpd.playlistadd', {name: this.selectedPlaylist.name, uri: resource});
            await this.refreshSelectedPlaylist();
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

        refreshSelectedPlaylist: async function() {
            if (!this.selectedPlaylist.name) {
                return;
            }

            let items = (await this.listplaylistinfo(this.selectedPlaylist.name)).map((_, i) => {
                return { ..._, pos: i }
            });

            Vue.set(this.selectedPlaylist, 'items', items);
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


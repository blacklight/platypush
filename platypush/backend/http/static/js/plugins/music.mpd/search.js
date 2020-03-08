Vue.component('music-mpd-search', {
    template: '#tmpl-music-mpd-search',
    props: ['mpd'],
    data: function() {
        return {
            visible: false,
            showResults: false,
            results: [],
            filter: '',
            selectionMode: false,
            selectedItems: {},

            query: {
                any: '',
                file: '',
                artist: '',
                title: '',
                album: '',
            },
        };
    },

    computed: {
        dropdownItems: function() {
            var self = this;
            var items = [];

            if (Object.keys(this.selectedItems).length === 1) {
                items.push(
                    {
                        text: 'Play',
                        icon: 'play',
                        click: async function() {
                            const item = Object.values(self.selectedItems)[0];
                            await self.mpd.add(item.file, position=0);
                            await self.mpd.playpos(0);
                            self.selectedItems = {};
                        },
                    },
                    {
                        text: 'Replace and play',
                        icon: 'play',
                        click: async function() {
                            await self.mpd.clear();

                            const item = Object.values(self.selectedItems)[0];
                            await self.mpd.add(item.file, position=0);
                            await self.mpd.playpos(0);
                            self.selectedItems = {};
                        },
                    }
                );
            }

            items.push(
                {
                    text: 'Add to queue',
                    icon: 'plus',
                    click: async function() {
                        const items = Object.values(self.selectedItems);
                        const promises = items.map(item => self.mpd.add(item.file));

                        await Promise.all(promises);
                        self.selectedItems = {};
                    },
                },
            );

            if (Object.values(this.selectedItems).filter(_ => _.time != null).length === Object.values(this.selectedItems).length) {
                items.push(
                    {
                        text: 'Add to playlist',
                        icon: 'list',
                        click: async function() {
                            self.mpd.addToPlaylistItems = Object.values(self.selectedItems).map(_ => _.file);
                            self.mpd.modalVisible.playlistAdd = true;
                            await self.mpd.listplaylists();
                            self.selectedItems = {};
                        },
                    },
                );
            }

            if (Object.keys(this.selectedItems).length === 1) {
                const item = Object.values(this.selectedItems)[0];

                if (item.artist && item.artist.length) {
                    items.push({
                        text: 'View artist',
                        icon: 'user',
                        click: async function() {
                            await self.mpd.searchArtist(item);
                            self.selectedItems = {};
                        }
                    });
                }

                if (item.album && item.album.length) {
                    items.push({
                        text: 'View album',
                        icon: 'compact-disc',
                        click: async function() {
                            await self.mpd.searchAlbum(item);
                            self.selectedItems = {};
                        },
                    });
                }

                items.push({
                    text: 'View info',
                    icon: 'info',
                    click: function() {
                        self.$emit('info', item);
                    },
                });
            }

            return items;
        },
    },

    methods: {
        search: async function() {
            const filter = Object.keys(this.query).reduce((query, key) => {
                if (this.query[key].length) {
                    query[key] = this.query[key];
                }

                return query;
            }, {});

            this.results = [];
            var results = await request('music.mpd.search', {filter: filter});

            this.results = results.sort((a,b) => {
                if (a.artist != b.artist)
                    return (a.artist || '').localeCompare(b.artist || '');
                if (a.album != b.album)
                    return (a.album || '').localeCompare(b.album || '');
                if (a.track != b.track)
                    return parseInt(a.track || 0) > parseInt(b.track || 0);
                if (a.title != b.title)
                    return (a.title || '').localeCompare(b.title || '');
                if (a.file != b.file)
                    return (a.file || '').localeCompare(b.file || '');
                return 0;
            });

            this.showResults = true;
        },

        matchesFilter: function(item) {
            if (this.filter.length === 0)
                return true;

            const filter = this.filter.split(' ').filter(_ => _.length > 0).map(_ => _.toLocaleLowerCase()).join(' ');
            return [item.file || '', item.artist || '', item.title || '', item.album || ''].join(' ').toLocaleLowerCase().indexOf(filter) >= 0;
        },

        onItemClick: function(item) {
            if (this.selectionMode) {
                if (item.file in this.selectedItems) {
                    Vue.delete(this.selectedItems, item.file);
                } else {
                    Vue.set(this.selectedItems, item.file, item);
                }
            } else if (item.file in this.selectedItems) {
                Vue.delete(this.selectedItems, item.file);
            } else {
                this.selectedItems = {};
                Vue.set(this.selectedItems, item.file, item);
                openDropdown(this.$refs.dropdown.$el);
            }
        },

        toggleSelectionMode: function() {
            if (this.selectionMode && Object.keys(this.selectedItems).length) {
                openDropdown(this.$refs.dropdown.$el);
            }

            this.selectionMode = !this.selectionMode;
        },

        selectAll: function() {
            this.selectedItems = {};
            this.selectionMode = true;

            for (var item of this.results) {
                this.selectedItems[item.file] = item;
            }

            openDropdown(this.$refs.dropdown.$el);
        },

        resetQuery: function() {
            this.filter = '';
            for (const attr of Object.keys(this.query)) {
                this.query[attr] = '';
            }
        },

        resetForm: function() {
            this.resetQuery();
            this.showResults = false;
            var self = this;

            setTimeout(() => {
                self.$refs.form.querySelector('input[type=text]:first-child').focus()
            }, 100)
        },
    },
});

Vue.component('music-mpd-search-item', {
    template: '#tmpl-music-mpd-search-item',
    mixins: [utils],
    props: {
        item: {
            type: Object,
            default: {},
        },

        selected: {
            type: Boolean,
            default: false,
        },
    },
});


Vue.component('music-mpd-search', {
    template: '#tmpl-music-mpd-search',
    props: ['mpd'],
    data: function() {
        return {
            visible: false,
            showResults: false,
            results: false,
            filter: '',
            selectionMode: false,
            selectedItems: {},

            query: {
                any: '',
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

            if (Object.keys(this.selectedItems).length === 1) {
                items.push({
                    text: 'View info',
                    icon: 'info',
                });
            }

            return items;
        },
    },

    methods: {
        search: async function() {
            const filter = Object.keys(this.query).reduce((items, key) => {
                if (this.query[key].length) {
                    items.push(key, this.query[key]);
                }

                return items;
            }, []);

            var results = await request('music.mpd.search', {filter: filter});
            this.results = results.sort((a,b) => {
                const tokenize = (t) => {
                    return ''.concat(t.artist || '', '-', t.album || '', '-', t.disc || '', '-', t.track || '', t.title || '').toLocaleLowerCase();
                };

                return tokenize(a).localeCompare(tokenize(b));
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
                this.selectedItems[item.id] = item;
            }

            openDropdown(this.$refs.dropdown.$el);
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


Vue.component('media-torrents', {
    template: '#tmpl-media-torrents',
    mixins: [mediaUtils],
    props: {
        bus: { type: Object },
        torrents: {
            type: Object,
            default: () => {},
        },
    },

    data: function() {
        return {
            selectedItem: undefined,
        };
    },

    computed: {
        dropdownItems: function() {
            const self = this;
            return [
                {
                    name: 'play',
                    text: 'Play',
                    iconClass: 'fa fa-play',
                    click: function() {
                        self.bus.$emit('torrent-play', self.selectedItem);
                    },
                },

                {
                    name: 'pause',
                    text: 'Pause/unpause transfer',
                    iconClass: 'fa fa-pause',
                    click: function() {
                        self.bus.$emit('torrent-pause', self.selectedItem);
                    },
                },

                {
                    name: 'cancel',
                    text: 'Cancel transfer',
                    iconClass: 'fa fa-trash',
                    click: function() {
                        self.bus.$emit('torrent-remove', self.selectedItem);
                    },
                },

                {
                    name: 'info',
                    text: 'View details',
                    iconClass: 'fa fa-info',
                    click: function() {
                        self.bus.$emit('info', self.selectedItem);
                    },
                },
            ];
        },
    },

    methods: {
        getTorrentPlugin: async function() {
            if (this.config && this.config.torrent_plugin) {
                return this.config.torrent_plugin;
            }

            const config = await request('inspect.get_config');
            if ('rtorrent' in config)
                return 'rtorrent';
            if ('webtorrent' in config)
                return 'webtorrent';
            return 'torrent'
        },

        openDropdown: function(item) {
            this.selectedItem = item;
            openDropdown(this.$refs.menu);
        },

        onMagnetDownload: async function() {
            const magnet = this.$refs.magnetLink.value.trim();
            if (!magnet.length)
                return;

            const torrentPlugin = await this.getTorrentPlugin();
            await request(torrentPlugin + '.download', {
                torrent: magnet,
                _async: true,
            });
        }
    },
});


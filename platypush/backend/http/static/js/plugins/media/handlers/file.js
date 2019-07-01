MediaHandlers.file = MediaHandlers.base.extend({
    props: {
        iconClass: {
            type: String,
            default: 'fa fa-hdd',
        },
    },

    computed: {
        dropdownItems: function() {
            return [
                {
                    text: 'Play',
                    icon: 'play',
                    action: this.play,
                },

                {
                    text: 'Play with subtitles',
                    iconClass: 'fas fa-closed-captioning',
                    action: this.searchSubtitles,
                },

                {
                    text: 'Download (on client)',
                    icon: 'download',
                    action: this.download,
                },

                {
                    text: 'View info',
                    icon: 'info',
                    action: this.info,
                },
            ];
        },
    },

    methods: {
        matchesUrl: function(url) {
            return !!url.match('^(file://)?/');
        },

        getMetadata: async function(item, onlyBase=false) {
            if (typeof item === 'string') {
                item = {
                    url: item,
                };
            }

            if (!item.path)
                item.path = item.url.startsWith('file://') ? item.url.substr(7) : item.url;

            if (!item.title)
                item.title = item.path.split('/').pop();

            if (!item.size && !onlyBase)
                item.size = await request('file.getsize', {filename: item.path});

            if (!item.duration && !onlyBase)
                item.duration = await request('media.get_media_file_duration', {filename: item.path});

            return item;
        },

        download: async function(item) {
            this.bus.$on('streaming-started', (media) => {
                if (media.resource === item.url) {
                    this.bus.$off('streaming-started');
                    window.open(media.url + '?download', '_blank');
                }
            });

            this.bus.$emit('start-streaming', item.url);
        },
    },
});

MediaHandlers.generic = MediaHandlers.file.extend({
    props: {
        iconClass: {
            type: String,
            default: 'fa fa-globe',
        },
    },

    computed: {
        dropdownItems: function() {
            return [
                {
                    text: 'Play',
                    icon: 'play',
                    action: this.play,
                },

                {
                    text: 'View info',
                    icon: 'info',
                    action: this.info,
                },
            ];
        },
    },

    methods: {
        getMetadata: async function(item) {
            return {
                url: item.url,
                title: item.url,
            };
        },
    },
});


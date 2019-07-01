MediaHandlers.youtube = MediaHandlers.base.extend({
    props: {
        iconClass: {
            type: String,
            default: 'fab fa-youtube',
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
                    text: 'Download (on server)',
                    icon: 'download',
                    action: this.downloadServer,
                },

                {
                    text: 'Download (on client)',
                    icon: 'download',
                    action: this.downloadClient,
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
            return !!(url.match('^https?://(www\.)?youtube.com/') || url.match('^https?://youtu.be/') || url.match('^https?://.*googlevideo.com/'));
        },

        getMetadata: function(item) {
            return {};
        },

        _getRawUrl: async function(url) {
            if (url.indexOf('.googlevideo.com') < 0) {
                url = await request('media.get_youtube_url', {url: url});
            }

            return url;
        },

        play: async function(item) {
            if (typeof item === 'string')
                item = {url: item};

            let url = await this._getRawUrl(item.url);
            this.bus.$emit('play', {...item, url:url});
        },

        downloadServer: async function(item) {
            createNotification({
                text: 'Downloading video',
                image: {
                    icon: 'download',
                },
            });

            let url = await this._getRawUrl(item.url);
            let args = {
                url: url,
            }

            if (item.title) {
                args.filename = item.title + '.webm';
            }

            let path = await request('media.download', args);

            createNotification({
                text: 'Video downloaded to ' + path,
                image: {
                    icon: 'check',
                },
            });
        },

        downloadClient: async function(item) {
            let url = await this._getRawUrl(item.url);
            window.open(url, '_blank');
        },
    },
});


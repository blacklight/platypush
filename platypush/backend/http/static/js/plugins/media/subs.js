Vue.component('media-subs', {
    template: '#tmpl-media-subs',
    props: {
        bus: { type: Object },
        subFormats: {
            type: Array,
            default: () => [],
        },
    },

    data: function() {
        return {
            loading: false,
            media: {},
            items: [],
            selectedItem: undefined,
        };
    },

    methods: {
        search: async function(media) {
            this.loading = true;

            this.media = media;
            this.selectedItem = undefined;
            this.items = await request('media.subtitles.get_subtitles', {resource: this.media.url});

            this.loading = false;
        },

        play: async function() {
            let args = {link: this.selectedItem.SubDownloadLink};

            if (this.media.url && this.media.url.startsWith('file://'))
                args.media_resource = this.media.url;

            if (this.subFormats.indexOf('srt') < 0)
                args.convert_to_vtt = true;

            this.media.subtitles = (await request('media.subtitles.download', args)).filename;
            this.bus.$emit('play', this.media);
        },
    },
});


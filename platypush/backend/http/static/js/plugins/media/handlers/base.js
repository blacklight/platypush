MediaHandlers.base = Vue.extend({
    props: {
        bus: { type: Object },
        iconClass: {
            type: String,
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
        matchesUrl: function(url) {
            return false;
        },

        getMetadata: async function(item, onlyBase=false) {
            return {};
        },

        play: function(item) {
            this.bus.$emit('play', item);
        },

        info: async function(item) {
            this.bus.$emit('info-loading');
            this.bus.$emit('info', {...item, ...(await this.getMetadata(item))});
        },

        infoLoad: function(url) {
            if (!this.matchesUrl(url))
                return;

            this.info(url);
        },

        searchSubtitles: function(item) {
            this.bus.$emit('search-subs', item);
        },
    },

    created: function() {
        const self = this;
        setTimeout(() => {
            self.infoLoadWatch = self.bus.$on('info-load', this.infoLoad);
        }, 1000);
    },
});


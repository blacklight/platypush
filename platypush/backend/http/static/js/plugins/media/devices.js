Vue.component('media-devices', {
    template: '#tmpl-media-devices',
    props: {
        bus: { type: Object },
    },

    data: function() {
        return {
            showDevicesMenu: false,
        };
    },

    computed: {
        dropdownItems: function() {
            var items = [
                {
                    text: 'Local player',
                    icon: 'desktop',
                },
                {
                    text: 'Browser',
                    icon: 'laptop',
                },
            ];

            return items;
        },
    },

    methods: {
        openDevicesMenu: function() {
            openDropdown(this.$refs.menu);
        },
    },

    created: function() {
    },
});


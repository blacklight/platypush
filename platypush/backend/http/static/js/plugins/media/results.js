Vue.component('media-results', {
    template: '#tmpl-media-results',
    props: {
        bus: { type: Object },
        searching: {
            type: Boolean,
            default: false,
        },
        loading: {
            type: Boolean,
            default: false,
        },
        results: {
            type: Array,
            default: () => [],
        },
        status: {
            type: Object,
            default: () => {},
        },
        resize: {
            type: Boolean,
            default: false,
        },
    },

    data: function() {
        return {
            selectedItem: {},
        };
    },

    computed: {
        mediaItemDropdownItems: function() {
            if (!Object.keys(this.selectedItem).length) {
                return [];
            }

            const self = this;

            return this.selectedItem.handler.dropdownItems.map(item => {
                return {
                    text: item.text,
                    icon: item.icon,
                    iconClass: item.iconClass,
                    click: function() {
                        item.action(self.selectedItem);
                    },
                };
            });
        },
    },

    methods: {
        itemClicked: function(item) {
            if (this.selectedItem.length && this.selectedItem.url === item.url) {
                return;
            }

            this.selectedItem = item;
            openDropdown(this.$refs.mediaItemDropdown);
        },
    },

    created: function() {
        this.bus.$on('result-clicked',  this.itemClicked);
    },
});


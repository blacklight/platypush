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
    },

    data: function() {
        return {
            selectedItem: {},
            currentItem: {},
        };
    },

    computed: {
        mediaItemDropdownItems: function() {
            if (!Object.keys(this.selectedItem).length) {
                return [];
            }

            const self = this;

            return this.selectedItem.handler.actions.map(action => {
                return {
                    text: action.text,
                    icon: action.icon,
                    click: function() {
                        if (action.action instanceof Function) {
                            action.action(self.selectedItem, self.bus);
                        } else if (typeof(action.action) === 'string') {
                            self[action.action](self.selectedItem);
                        }
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

        play: function(item) {
            this.bus.$emit('play', item);
        },

        info: function(item) {
            this.bus.$emit('info', item);
        },
    },

    created: function() {
        this.bus.$on('result-clicked',  this.itemClicked);
    },
});


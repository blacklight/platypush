Vue.component('modal', {
    template: '#tmpl-modal',
    props: {
        id: {
            type: String,
        },

        title: {
            type: String,
        },

        width: {
            type: [Number, String],
        },

        height: {
            type: [Number, String],
        },

        // Modal visibility value
        value: {
            type: Boolean,
            default: false,
        },

        timeout: {
            type: [Number, String],
        },

        level: {
            type: Number,
            default: 1,
        },
    },

    data: function() {
        return {
            timeoutId: undefined,
            prevValue: this.value,
        };
    },

    computed: {
        zIndex: function() {
            return 500 + this.level;
        },
    },

    methods: {
        modalClicked: function(event) {
            // Close any opened dropdowns before stopping the click propagation
            const dropdowns = this.$el.querySelectorAll('.dropdown:not(.hidden)');
            for (const dropdown of dropdowns) {
                closeDropdown(dropdown);
            }

            event.stopPropagation();
        },

        modalClose: function() {
            event.stopPropagation();
            this.$emit('input', false);
        },
    },

    updated: function() {
        if (this.value != this.prevValue) {
            this.$emit((this.value ? 'open' : 'close'), this);
            this.prevValue = this.value;
        }

        if (this.value && this.timeout && !this.timeoutId) {
            var handler = (self) => {
                return () => {
                    self.modalClose();
                    self.timeoutId = undefined;
                };
            };

            this.timeoutId = setTimeout(handler(this), 0+this.timeout);
        }
    },
});


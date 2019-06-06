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

        if (this.value) {
            // Make sure that a newly opened or visible+updated modal always comes to the front
            const myZIndex = parseInt(getComputedStyle(this.$el).zIndex);
            var maxZIndex = myZIndex;
            var outermostModals = [];

            for (const modal of document.querySelectorAll('.modal-container:not(.hidden)')) {
                const zIndex = parseInt(getComputedStyle(modal).zIndex);

                if (zIndex > maxZIndex) {
                    maxZIndex = zIndex;
                    outermostModals = [modal];
                } else if (zIndex == maxZIndex) {
                    outermostModals.push(modal);
                }
            }

            if (outermostModals.indexOf(this.$el) < 0 || outermostModals.length > 1) {
                this.$el.style.zIndex = maxZIndex+1;
            }
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


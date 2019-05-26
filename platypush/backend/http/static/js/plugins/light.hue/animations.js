Vue.component('light-hue-animations-container', {
    template: '#tmpl-light-hue-animations-container',
    props: ['groupId','animation','collapsed'],
    data: function() {
        return {
            selectedAnimation: 'color_transition',
        };
    },

    methods: {
        animationsCollapsedToggled: function() {
            this.$emit('animations-collapsed-toggled', {
                type: 'animation',
                id: this.groupId,
            });
        },
        toggled: async function(event) {
            if (event.value) {
                var args = {
                    ...this.$refs[this.selectedAnimation].value,
                    animation: this.selectedAnimation,
                    groups: [this.groupId],
                }

                await request('light.hue.on', {groups: [this.groupId]});
                await request('light.hue.animate', args);

                this.$emit('animation-started', {
                    ...this.$refs[this.selectedAnimation].value,
                    type: this.selectedAnimation,
                });
            } else {
                await request('light.hue.stop_animation');
                this.$emit('animation-stopped', {});
            }
        },
    },
});


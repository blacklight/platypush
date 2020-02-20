Vue.component('toggle-switch', {
    template: '#tmpl-switch',
    props: ['id','value','glow'],

    methods: {
        toggled: function(event) {
            this.$emit('toggled', {
                id: this.id,
                value: !this.value,
                event: event,
            });
        },
    },
});


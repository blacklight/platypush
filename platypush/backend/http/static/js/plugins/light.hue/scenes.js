Vue.component('light-hue-scene', {
    template: '#tmpl-light-hue-scene',
    props: ['id','name'],

    methods: {
        clicked: function(event) {
            this.$emit('input', {id: this.id, name: this.name});
        },
    },
});


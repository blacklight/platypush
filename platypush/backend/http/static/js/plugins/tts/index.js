Vue.component('tts', {
    template: '#tmpl-tts',
    data: function() {
        return {
            talking: false,
        };
    },

    methods: {
        talk: async function(event) {
            event.preventDefault();

            const args = [...event.target.querySelectorAll('input')].reduce((obj, el) => {
                if (el.value.length)
                    obj[el.name] = el.value;
                return obj;
            }, {});

            this.talking = true;
            await request('tts.say', args);
            this.talking = false;
        },
    },
});


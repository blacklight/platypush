Vue.component('tts-google', {
    template: '#tmpl-tts-google',
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
            await request('tts.google.say', args);
            this.talking = false;
        },
    },
});



Vue.component('app-header', {
    template: '#tmpl-app-header',
    data: function() {
        return {
            now: new Date(),
        };
    },

    created: function() {
        const self = this;
        setInterval(() => {
            self.now = new Date();
        }, 1000)
    },
});

Vue.component('plugin', {
    template: '#tmpl-plugin',
    props: ['config','tag'],

    data: function() {
        return {
            selected: false,
        };
    },
});

// Declaration of the main vue app
window.vm = new Vue({
    el: '#app',
    // Override {{ }} delimiters to prevent clash with Flask templates
    delimiters: ['[[',']]'],

    data: function() {
        return {
            config: window.config,
            selectedPlugin: undefined,
            now: new Date(),
        };
    },

    created: function() {
        const self = this;
        setInterval(() => {
            self.now = new Date();
        }, 1000)

        initEvents();
    },
});

